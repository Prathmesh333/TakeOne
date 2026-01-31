"""
Pipeline Orchestrator - Complete video processing pipeline
Combines scene detection, clipping, Gemini analysis, and indexing
"""

import os
import json
import logging
import re
from pathlib import Path
from typing import List, Dict, Optional, Callable
from datetime import datetime
from dotenv import load_dotenv

# Suppress progress bars from sentence-transformers and other libraries (works with all versions)
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TakeOnePipeline:
    """
    Complete video processing pipeline for TakeOne.
    
    Stages:
    1. Scene Detection - Find natural scene boundaries
    2. Clip Extraction - Extract scene clips and thumbnails
    3. Gemini Analysis - Analyze clips with VLM
    4. Indexing - Store in vector database for search
    """
    
    def __init__(
        self,
        output_dir: str = "./output",
        clips_dir: str = None,
        thumbnails_dir: str = None,
        chroma_dir: str = "./chroma_db",
        gemini_model: str = "gemini-2.5-flash"
    ):
        """
        Initialize the pipeline.
        
        Args:
            output_dir: Base directory for outputs
            clips_dir: Directory for clips (default: output_dir/clips)
            thumbnails_dir: Directory for thumbnails (default: output_dir/thumbnails)
            chroma_dir: ChromaDB storage directory
            gemini_model: Gemini model to use
        """
        self.output_dir = Path(output_dir)
        self.clips_dir = Path(clips_dir) if clips_dir else self.output_dir / "clips"
        self.thumbnails_dir = Path(thumbnails_dir) if thumbnails_dir else self.output_dir / "thumbnails"
        self.chroma_dir = Path(chroma_dir)
        self.gemini_model = gemini_model
        
        # Create directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.clips_dir.mkdir(parents=True, exist_ok=True)
        self.thumbnails_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components lazily
        self._analyzer = None
        self._search_engine = None
        
        logger.info(f"TakeOne Pipeline initialized")
        logger.info(f"  Output: {self.output_dir}")
        logger.info(f"  Clips: {self.clips_dir}")
        logger.info(f"  Model: {gemini_model}")
    
    @property
    def analyzer(self):
        """Lazy-load Gemini analyzer."""
        if self._analyzer is None:
            from ingestion.gemini_analyzer import GeminiAnalyzer
            self._analyzer = GeminiAnalyzer(model_name=self.gemini_model)
        return self._analyzer
    
    @property
    def search_engine(self):
        """Lazy-load search engine."""
        if self._search_engine is None:
            from search.vector_search import SceneSearchEngine
            self._search_engine = SceneSearchEngine(persist_dir=str(self.chroma_dir))
        return self._search_engine
    
    def process_video(
        self,
        video_path: str,
        video_id: Optional[str] = None,
        scene_threshold: float = 27.0,
        max_scene_duration: float = 10.0,
        min_scene_duration: float = 2.0,
        skip_analysis: bool = False,
        skip_indexing: bool = False,
        use_yolo: bool = True,
        yolo_scene_detection: bool = True,
        cleanup_download: bool = True,
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> Dict:
        """
        Process a video through the complete pipeline.
        
        Args:
            video_path: Path to input video OR URL (YouTube, Google Drive, direct link, etc.)
            video_id: Unique identifier (uses filename if not provided)
            scene_threshold: Scene detection sensitivity (for PySceneDetect: higher=fewer scenes, for YOLO: 0-1 lower=more scenes)
            max_scene_duration: Max scene length before splitting
            min_scene_duration: Min scene length before merging
            skip_analysis: Skip Gemini analysis (for testing)
            skip_indexing: Skip vector indexing
            use_yolo: Use YOLO for frame selection (provides context to Gemini)
            yolo_scene_detection: Use YOLO for semantic scene detection (faster and semantically aware)
            cleanup_download: Delete downloaded file after processing (if URL was provided)
            progress_callback: Callback(stage, current, total) for progress
            
        Returns:
            Dict with processing results and statistics
        """
        from ingestion.scene_detector import detect_scenes_hybrid, smart_split_scenes, get_scene_stats
        from ingestion.video_clipper import (
            extract_all_clips, extract_thumbnails_batch, get_video_info
        )
        from ingestion.video_downloader import VideoDownloader
        
        # Check if input is URL
        downloader = VideoDownloader(download_dir=str(self.output_dir / "downloads"))
        is_url = downloader.is_url(video_path)
        downloaded_file = None
        original_url = None
        
        if is_url:
            logger.info(f"Detected URL input: {video_path}")
            logger.info("Downloading video...")
            original_url = video_path
            
            try:
                downloaded_file, metadata = downloader.download(video_path)
                video_path = downloaded_file
                
                # Use metadata for video_id if not provided
                if not video_id and metadata.get('title'):
                    # Sanitize title for use as ID
                    video_id = re.sub(r'[^\w\s-]', '', metadata['title'])
                    video_id = re.sub(r'[-\s]+', '_', video_id)
                
                logger.info(f"Download complete: {video_path}")
                logger.info(f"Video title: {metadata.get('title', 'Unknown')}")
                
            except Exception as e:
                logger.error(f"Failed to download video: {e}")
                raise
        
        video_path = Path(video_path)
        video_id = video_id or video_path.stem
        
        logger.info(f"{'='*60}")
        logger.info(f"Processing: {video_path.name}")
        logger.info(f"Video ID: {video_id}")
        logger.info(f"YOLO Scene Detection: {'Enabled' if yolo_scene_detection else 'Disabled'}")
        logger.info(f"YOLO Frame Selection: {'Enabled' if use_yolo else 'Disabled'}")
        logger.info(f"{'='*60}")
        
        results = {
            "video_id": video_id,
            "video_path": str(video_path),
            "status": "processing",
            "stages": {},
            "error": None,
            "yolo_enabled": use_yolo or yolo_scene_detection,
            "downloaded_from_url": is_url,
            "original_url": original_url if is_url else None
        }
        
        try:
            # Get video info
            video_info = get_video_info(str(video_path))
            if video_info:
                results["video_info"] = video_info
                logger.info(f"Video: {video_info['width']}x{video_info['height']}, "
                          f"{video_info['duration']:.1f}s")
            
            # Stage 1: Scene Detection
            logger.info("\n[Stage 1] Scene Detection")
            if progress_callback:
                progress_callback("Scene Detection", 0, 1)
            
            # Check GPU availability
            import torch
            use_gpu = torch.cuda.is_available()
            
            # Use YOLO or PySceneDetect based on flag
            if yolo_scene_detection:
                # YOLO threshold is 0-1 (semantic similarity), convert if needed
                yolo_threshold = scene_threshold if scene_threshold <= 1.0 else 0.4
                raw_scenes = detect_scenes_hybrid(
                    str(video_path),
                    use_yolo=True,
                    use_gpu=use_gpu,
                    threshold=yolo_threshold,
                    min_scene_len=min_scene_duration,
                    sample_rate=5  # Process every 5th frame for speed
                )
                detection_method = "YOLO (GPU)" if use_gpu else "YOLO (CPU)"
            else:
                raw_scenes = detect_scenes_hybrid(
                    str(video_path),
                    use_yolo=False,
                    threshold=scene_threshold,
                    min_scene_len=min_scene_duration
                )
                detection_method = "PySceneDetect"
            
            scenes = smart_split_scenes(
                raw_scenes,
                max_duration=max_scene_duration,
                min_duration=min_scene_duration
            )
            
            scene_stats = get_scene_stats(scenes)
            results["stages"]["scene_detection"] = {
                "method": detection_method,
                "raw_scenes": len(raw_scenes),
                "optimized_scenes": len(scenes),
                "stats": scene_stats
            }
            
            logger.info(f"  Method: {detection_method}")
            logger.info(f"  Found {len(raw_scenes)} raw scenes → {len(scenes)} optimized clips")
            
            if progress_callback:
                progress_callback("Scene Detection", 1, 1)
            
            # Stage 2: Clip Extraction
            logger.info("\n[Stage 2] Clip Extraction")
            logger.info(f"  Extracting {len(scenes)} clips with FFmpeg...")
            if progress_callback:
                progress_callback("Clip Extraction", 0, len(scenes))
            
            clips = extract_all_clips(
                str(video_path),
                scenes,
                str(self.clips_dir),
                video_id=video_id
            )
            
            results["stages"]["clip_extraction"] = {
                "clips_created": len(clips),
                "clips_total": len(scenes)
            }
            
            logger.info(f"  ✅ Extracted {len(clips)}/{len(scenes)} clips")
            
            if progress_callback:
                progress_callback("Clip Extraction", len(clips), len(scenes))
            
            # Stage 3: Thumbnail Extraction with YOLO Context
            logger.info("\n[Stage 3] Thumbnail Extraction")
            logger.info(f"  Generating thumbnails for {len(clips)} clips...")
            if progress_callback:
                progress_callback("Thumbnails", 0, len(clips))
            
            clips = extract_thumbnails_batch(
                str(video_path),
                clips,
                str(self.thumbnails_dir),
                video_id=video_id,
                use_yolo=use_yolo
            )
            
            thumbs_created = sum(1 for c in clips if c.get('thumbnail_path'))
            yolo_contexts = sum(1 for c in clips if c.get('yolo_context'))
            
            results["stages"]["thumbnails"] = {
                "created": thumbs_created,
                "total": len(clips),
                "with_yolo_context": yolo_contexts
            }
            
            logger.info(f"  ✅ Generated {thumbs_created} thumbnails")
            if yolo_contexts > 0:
                logger.info(f"  ✅ YOLO context available for {yolo_contexts} clips")
            
            if progress_callback:
                progress_callback("Thumbnails", thumbs_created, len(clips))
            
            # Stage 4: Gemini Analysis (All clips)
            if not skip_analysis:
                logger.info("\n[Stage 4] Gemini Analysis")
                logger.info(f"  Analyzing {len(clips)} clips with Gemini (using thumbnails)")
                
                def analysis_progress(current, total):
                    logger.info(f"  Progress: {current}/{total} ({current/total*100:.0f}%) - Gemini analysis")
                    if progress_callback:
                        progress_callback("Gemini Analysis", current, total)
                
                # Use thumbnails for Gemini analysis
                gemini_clips = []
                for clip in clips:
                    # Create a DEEP COPY to avoid modifying original clip_info
                    gemini_clip_info = clip.copy()
                    
                    # Use thumbnail image instead of video clip
                    if gemini_clip_info.get('thumbnail_path'):
                        thumb_path = Path(gemini_clip_info['thumbnail_path'])
                        
                        # Verify thumbnail exists
                        if thumb_path.exists():
                            # Replace clip_path with thumbnail_path for Gemini ONLY
                            # This does NOT affect the original clip dict
                            gemini_clip_info['clip_path'] = str(thumb_path)
                            gemini_clip_info['is_thumbnail'] = True
                            logger.debug(f"Using thumbnail for Gemini: {thumb_path.name}")
                        else:
                            logger.error(f"Thumbnail missing: {thumb_path}, skipping clip")
                            continue  # Skip this clip
                    else:
                        logger.warning(f"No thumbnail for clip {gemini_clip_info.get('clip_path')}, skipping")
                        continue  # Skip clips without thumbnails
                    
                    gemini_clips.append(gemini_clip_info)
                
                logger.info(f"  Sending {len(gemini_clips)} thumbnails (images) to Gemini")
                
                analysis_results = self.analyzer.analyze_clips_batch(
                    gemini_clips,
                    progress_callback=analysis_progress
                )
                
                # CRITICAL FIX: Restore original clip paths from 'clips' list
                # The gemini_clips had thumbnail paths, but we need video clip paths for indexing
                for i, result in enumerate(analysis_results):
                    if result.get('status') == 'success' and result.get('clip_info'):
                        clip_index = result['clip_info'].get('clip_index')
                        # Find original clip by index
                        original_clip = next((c for c in clips if c.get('clip_index') == clip_index), None)
                        if original_clip:
                            # Restore the ORIGINAL clip_path (video .mp4, not thumbnail .jpg)
                            result['clip_info']['clip_path'] = original_clip['clip_path']
                            logger.debug(f"Restored clip path: {original_clip['clip_path']}")
                
                success_count = sum(1 for r in analysis_results if r['status'] == 'success')
                
                results["stages"]["analysis"] = {
                    "successful": success_count,
                    "failed": len(analysis_results) - success_count,
                    "total": len(analysis_results),
                    "method": "gemini"
                }
                
                logger.info(f"  Gemini analysis: {success_count}/{len(analysis_results)} successful")
                
                # Save analysis results
                analysis_file = self.output_dir / f"{video_id}_analysis.json"
                with open(analysis_file, 'w', encoding='utf-8') as f:
                    json.dump(analysis_results, f, indent=2, ensure_ascii=False)
                results["analysis_file"] = str(analysis_file)
                
            else:
                analysis_results = []
                results["stages"]["analysis"] = {"skipped": True}
            
            # Stage 5: Indexing
            if not skip_indexing and analysis_results:
                logger.info("\n[Stage 5] Vector Indexing")
                if progress_callback:
                    progress_callback("Indexing", 0, 1)
                
                indexed = self.search_engine.index_scenes(analysis_results)
                
                results["stages"]["indexing"] = {
                    "indexed": indexed,
                    "total": len(analysis_results)
                }
                
                logger.info(f"  Indexed {indexed} scenes")
                
                if progress_callback:
                    progress_callback("Indexing", 1, 1)
            else:
                results["stages"]["indexing"] = {"skipped": True}
            
            # Complete
            results["status"] = "complete"
            results["completed_at"] = datetime.now().isoformat()
            
            logger.info(f"\n{'='*60}")
            logger.info("Processing complete successfully")
            logger.info(f"{'='*60}")
            
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            results["status"] = "error"
            results["error"] = str(e)
            raise
        
        finally:
            # Cleanup downloaded file if requested
            if is_url and downloaded_file and cleanup_download:
                logger.info("Cleaning up downloaded file...")
                downloader.cleanup(downloaded_file)
        
        return results
    
    def process_videos(
        self,
        video_paths: List[str],
        progress_callback: Optional[Callable[[str, str, int, int], None]] = None,
        **kwargs
    ) -> List[Dict]:
        """
        Process multiple videos.
        
        Args:
            video_paths: List of video paths
            progress_callback: Callback(video_name, stage, current, total)
            **kwargs: Additional arguments passed to process_video
            
        Returns:
            List of processing results
        """
        results = []
        
        for i, video_path in enumerate(video_paths):
            video_name = Path(video_path).name
            logger.info(f"\n[{i+1}/{len(video_paths)}] Processing: {video_name}")
            
            def video_progress(stage, current, total):
                if progress_callback:
                    progress_callback(video_name, stage, current, total)
            
            try:
                result = self.process_video(
                    video_path,
                    progress_callback=video_progress,
                    **kwargs
                )
                results.append(result)
            except Exception as e:
                results.append({
                    "video_path": video_path,
                    "status": "error",
                    "error": str(e)
                })
        
        return results
    
    def search(self, query: str, top_k: int = 10, **kwargs) -> List[Dict]:
        """
        Search indexed scenes.
        
        Args:
            query: Natural language search query
            top_k: Number of results
            **kwargs: Additional filters
            
        Returns:
            List of matching scenes
        """
        return self.search_engine.search(query, top_k=top_k, **kwargs)
    
    def get_stats(self) -> Dict:
        """Get pipeline statistics."""
        return {
            "search_engine": self.search_engine.get_stats(),
            "output_dir": str(self.output_dir),
            "clips_dir": str(self.clips_dir),
            "model": self.gemini_model
        }


def main():
    """CLI for the pipeline."""
    import argparse
    
    parser = argparse.ArgumentParser(description="TakeOne Video Processing Pipeline")
    parser.add_argument("video", help="Path to video file or directory")
    parser.add_argument("--output", "-o", default="./output", help="Output directory")
    parser.add_argument("--model", "-m", default="gemini-2.5-flash", help="Gemini model")
    parser.add_argument("--threshold", "-t", type=float, default=0.4, help="Scene detection threshold (YOLO: 0-1, PySceneDetect: 1-100)")
    parser.add_argument("--skip-analysis", action="store_true", help="Skip Gemini analysis")
    parser.add_argument("--skip-indexing", action="store_true", help="Skip vector indexing")
    parser.add_argument("--use-yolo", action="store_true", default=True, help="Use YOLO frame selection (default: True)")
    parser.add_argument("--no-yolo", action="store_true", help="Disable YOLO frame selection")
    parser.add_argument("--yolo-scenes", action="store_true", default=True, help="Use YOLO for scene detection (default: True)")
    parser.add_argument("--no-yolo-scenes", action="store_true", help="Use PySceneDetect instead of YOLO")
    
    args = parser.parse_args()
    
    # Handle YOLO flags
    use_yolo = args.use_yolo and not args.no_yolo
    yolo_scenes = args.yolo_scenes and not args.no_yolo_scenes
    
    # Check API key
    if not os.environ.get("GEMINI_API_KEY") and not args.skip_analysis:
        print("ERROR: GEMINI_API_KEY not set. Use --skip-analysis or set the environment variable.")
        return
    
    # Initialize pipeline
    pipeline = TakeOnePipeline(
        output_dir=args.output,
        gemini_model=args.model
    )
    
    # Process video(s)
    video_path = Path(args.video)
    
    if video_path.is_dir():
        videos = list(video_path.glob("*.mp4")) + list(video_path.glob("*.mov"))
        print(f"Found {len(videos)} videos")
        results = pipeline.process_videos(
            [str(v) for v in videos],
            scene_threshold=args.threshold,
            skip_analysis=args.skip_analysis,
            skip_indexing=args.skip_indexing,
            use_yolo=use_yolo,
            yolo_scene_detection=yolo_scenes
        )
    else:
        results = [pipeline.process_video(
            str(video_path),
            scene_threshold=args.threshold,
            skip_analysis=args.skip_analysis,
            skip_indexing=args.skip_indexing,
            use_yolo=use_yolo,
            yolo_scene_detection=yolo_scenes
        )]
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for r in results:
        status = "SUCCESS" if r["status"] == "complete" else "FAILED"
        print(f"[{status}] {r.get('video_id', 'unknown')}: {r['status']}")
        if r.get('yolo_enabled'):
            print(f"   YOLO: Enabled")
        if r.get('stages', {}).get('scene_detection', {}).get('method'):
            print(f"   Scene Detection: {r['stages']['scene_detection']['method']}")


if __name__ == "__main__":
    main()
