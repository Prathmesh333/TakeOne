"""
Video Clipper - Extracts scene clips from videos using FFmpeg
Supports parallel extraction and thumbnail generation
"""

import subprocess
import os
from pathlib import Path
from typing import List, Tuple, Optional, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

logger = logging.getLogger(__name__)


def extract_clip(
    video_path: str,
    start_time: float,
    end_time: float,
    output_path: str,
    quality: str = "medium"
) -> Optional[str]:
    """
    Extract a single clip from video using FFmpeg with maximum speed optimization.
    
    Args:
        video_path: Source video path
        start_time: Start time in seconds
        end_time: End time in seconds
        output_path: Output file path
        quality: Encoding quality - "fast", "medium", or "high"
        
    Returns:
        Path to created clip, or None on failure
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    duration = end_time - start_time
    
    # Ultra-fast presets optimized for speed
    presets = {
        "fast": {"preset": "ultrafast", "crf": "28", "tune": "fastdecode"},
        "medium": {"preset": "ultrafast", "crf": "23", "tune": "fastdecode"},
        "high": {"preset": "veryfast", "crf": "18", "tune": "fastdecode"}
    }
    preset = presets.get(quality, presets["medium"])
    
    # Maximum speed optimization flags
    cmd = [
        'ffmpeg', '-y',
        '-ss', str(start_time),  # Seek before input (faster)
        '-i', str(video_path),
        '-t', str(duration),
        '-c:v', 'libx264',
        '-preset', preset["preset"],
        '-crf', preset["crf"],
        '-tune', preset["tune"],
        '-threads', '0',  # Use all available CPU threads
        '-c:a', 'aac',
        '-b:a', '128k',
        '-movflags', '+faststart',
        '-max_muxing_queue_size', '1024',  # Prevent buffer issues
        '-loglevel', 'error',
        str(output_path)
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        logger.debug(f"Extracted clip: {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        logger.error(f"Error extracting clip: {e.stderr.decode() if e.stderr else str(e)}")
        return None
    except FileNotFoundError:
        logger.error("FFmpeg not found. Please install FFmpeg and add to PATH.")
        return None


def extract_all_clips(
    video_path: str,
    scenes: List[Tuple[float, float]],
    output_dir: str,
    video_id: Optional[str] = None,
    max_workers: int = 8,  # Increased from 4 for faster parallel processing
    quality: str = "medium"
) -> List[Dict]:
    """
    Extract all scene clips from a video with maximum speed optimization.
    
    Args:
        video_path: Source video path
        scenes: List of (start, end) tuples
        output_dir: Directory for output clips
        video_id: Identifier for the video (uses filename if not provided)
        max_workers: Number of parallel extractions (increased to 8 for speed)
        quality: Encoding quality
        
    Returns:
        List of clip info dicts
    """
    video_path = Path(video_path)
    video_id = video_id or video_path.stem
    clip_output_dir = Path(output_dir) / video_id
    clip_output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Extracting {len(scenes)} clips from {video_path.name}")
    
    def extract_single(args):
        idx, (start, end) = args
        clip_filename = f"scene_{idx:04d}.mp4"
        clip_path = str(clip_output_dir / clip_filename)
        
        result = extract_clip(str(video_path), start, end, clip_path, quality)
        
        if result:
            return {
                'clip_index': idx,
                'clip_path': clip_path,
                'clip_filename': clip_filename,
                'start_time': start,
                'end_time': end,
                'duration': end - start,
                'video_id': video_id,
                'source_video': str(video_path.absolute())
            }
        return None
    
    clip_infos = []
    completed = 0
    total = len(scenes)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(extract_single, (i, scene)): i 
                   for i, scene in enumerate(scenes)}
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                clip_infos.append(result)
            
            completed += 1
            # Log progress every 10% or every 10 clips
            if completed % max(1, total // 10) == 0 or completed % 10 == 0:
                logger.info(f"  Clip extraction progress: {completed}/{total} ({completed/total*100:.0f}%)")
    
    # Sort by clip index
    clip_infos.sort(key=lambda x: x['clip_index'])
    
    logger.info(f"Successfully extracted {len(clip_infos)}/{len(scenes)} clips")
    return clip_infos


def extract_thumbnail(
    video_path: str,
    time_point: float,
    output_path: str,
    size: str = "320x180"
) -> Optional[str]:
    """
    Extract a thumbnail from video at specified time with maximum speed.
    
    Args:
        video_path: Source video path
        time_point: Time in seconds
        output_path: Output image path (.jpg recommended)
        size: Thumbnail dimensions (WxH)
        
    Returns:
        Path to created thumbnail, or None on failure
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Ultra-fast thumbnail extraction
    cmd = [
        'ffmpeg', '-y',
        '-ss', str(time_point),  # Seek before input (faster)
        '-i', str(video_path),
        '-vframes', '1',
        '-vf', f'scale={size}:flags=fast_bilinear',  # Fast scaling algorithm
        '-q:v', '2',
        '-threads', '1',  # Single thread is faster for single frame
        '-loglevel', 'error',
        str(output_path)
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path
    except subprocess.CalledProcessError as e:
        logger.error(f"Error extracting thumbnail: {e.stderr.decode() if e.stderr else str(e)}")
        return None


def extract_thumbnails_batch(
    video_path: str,
    clips: List[Dict],
    output_dir: str,
    video_id: Optional[str] = None,
    max_workers: int = 8,  # Increased from 4 for faster parallel processing
    use_yolo: bool = False
) -> List[Dict]:
    """
    Extract thumbnails for all clips with optional YOLO context and maximum speed.
    
    Args:
        video_path: Source video path
        clips: List of clip info dicts (must have start_time, end_time, clip_index)
        output_dir: Directory for thumbnails
        video_id: Video identifier
        max_workers: Parallel extractions (increased to 8 for speed)
        use_yolo: Whether to use YOLO-based frame selection with context
        
    Returns:
        Updated clips list with thumbnail_path and yolo_context added
    """
    video_path = Path(video_path)
    video_id = video_id or video_path.stem
    thumb_dir = Path(output_dir) / video_id
    thumb_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize frame selector if needed
    frame_selector = None
    if use_yolo:
        try:
            from ingestion.frame_selector import FrameSelector, save_frame
            frame_selector = FrameSelector()
            # Force load model 
            _ = frame_selector.model
            logger.info("YOLO frame selector initialized")
        except Exception as e:
            logger.warning(f"Failed to load FrameSelector: {e}. Falling back to standard extraction.")
            use_yolo = False

    def extract_single(clip):
        thumb_filename = f"scene_{clip['clip_index']:04d}.jpg"
        thumb_path = str(thumb_dir / thumb_filename)
        
        result = None
        yolo_context = None
        
        if use_yolo and frame_selector:
            # Smart selection with YOLO context
            logger.debug(f"Smart selecting frame for scene {clip['clip_index']}")
            frame_data = frame_selector.select_best_frame(
                str(video_path), 
                clip['start_time'], 
                clip['end_time']
            )
            if frame_data:
                if save_frame(frame_data, thumb_path):
                    result = thumb_path
                # Extract YOLO detections for Gemini context
                yolo_context = {
                    'objects_detected': [d['class_name'] for d in frame_data.get('detections', [])],
                    'num_objects': len(frame_data.get('detections', [])),
                    'confidence_avg': sum(d['confidence'] for d in frame_data.get('detections', [])) / len(frame_data.get('detections', [])) if frame_data.get('detections') else 0
                }
        
        if not result:
            # Fallback / Standard: Middle of clip
            mid_time = clip['start_time'] + (clip['duration'] / 2)
            result = extract_thumbnail(str(video_path), mid_time, thumb_path)
        
        if result:
            clip['thumbnail_path'] = thumb_path
            clip['thumbnail_filename'] = thumb_filename
            if yolo_context:
                clip['yolo_context'] = yolo_context
        
        return clip
    
    # Use ThreadPool only if NOT using YOLO (standard) or if YOLO is GPU safe/efficient
    if use_yolo:
        logger.info("Extracting thumbnails with YOLO context (Sequential)...")
        return [extract_single(c) for c in clips]
    else:
        logger.info("Extracting thumbnails (Parallel)...")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            clips = list(executor.map(extract_single, clips))
    
    return clips


def get_video_info(video_path: str) -> Optional[Dict]:
    """
    Get video metadata using FFprobe.
    
    Args:
        video_path: Path to video file
        
    Returns:
        Dict with video info, or None on failure
    """
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height,duration,r_frame_rate',
        '-show_entries', 'format=duration,size',
        '-of', 'json',
        str(video_path)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        import json
        data = json.loads(result.stdout)
        
        stream = data.get('streams', [{}])[0]
        format_info = data.get('format', {})
        
        # Parse frame rate
        fps_str = stream.get('r_frame_rate', '30/1')
        if '/' in fps_str:
            num, den = map(int, fps_str.split('/'))
            fps = num / den if den != 0 else 30
        else:
            fps = float(fps_str)
        
        return {
            'width': int(stream.get('width', 0)),
            'height': int(stream.get('height', 0)),
            'duration': float(format_info.get('duration', 0)),
            'size_bytes': int(format_info.get('size', 0)),
            'fps': fps,
            'path': str(Path(video_path).absolute())
        }
    except Exception as e:
        logger.error(f"Error getting video info: {e}")
        return None


if __name__ == "__main__":
    import sys
    from scene_detector import detect_scenes, smart_split_scenes
    
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
        print(f"Processing: {video_path}")
        
        # Get video info
        info = get_video_info(video_path)
        if info:
            print(f"Video: {info['width']}x{info['height']}, {info['duration']:.1f}s, {info['fps']:.1f}fps")
        
        # Detect and optimize scenes
        scenes = detect_scenes(video_path)
        scenes = smart_split_scenes(scenes)
        print(f"Found {len(scenes)} scenes to extract")
        
        # Extract clips
        clips = extract_all_clips(video_path, scenes, "./clips")
        print(f"Extracted {len(clips)} clips")
        
        # Extract thumbnails
        clips = extract_thumbnails_batch(video_path, clips, "./thumbnails")
        print(f"Generated thumbnails")
        
        # Show first few
        for clip in clips[:5]:
            print(f"  Scene {clip['clip_index']}: {clip['duration']:.1f}s - {clip['clip_path']}")
    else:
        print("Usage: python video_clipper.py <video_path>")
