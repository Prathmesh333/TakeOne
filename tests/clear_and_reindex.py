"""
Clear Database and Re-index Videos

This script clears the current ChromaDB database and re-processes all videos
in the output/clips directory to rebuild the index with correct paths.

Usage:
    python clear_and_reindex.py
"""

import os
import sys
from pathlib import Path
import logging
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

def main():
    """Clear database and re-index all videos."""
    
    # Check for API key
    if not os.environ.get("GEMINI_API_KEY"):
        print("ERROR: GEMINI_API_KEY not set in .env file")
        print("Please add your Gemini API key to continue.")
        return 1
    
    # Import after env is loaded
    from search.vector_search import SceneSearchEngine
    from ingestion.pipeline import TakeOnePipeline
    
    print("="*60)
    print("CLEAR DATABASE AND RE-INDEX")
    print("="*60)
    
    # Initialize search engine
    search_engine = SceneSearchEngine(persist_dir="./chroma_db")
    
    # Get current stats
    stats = search_engine.get_stats()
    print(f"\nCurrent database:")
    print(f"  Total scenes: {stats['total_scenes']}")
    print(f"  Unique videos: {stats['unique_videos']}")
    
    # Confirm with user
    print("\n⚠️  WARNING: This will:")
    print("  1. Archive the current database")
    print("  2. Create a new empty database")
    print("  3. Re-process all videos found in output/clips/")
    
    response = input("\nContinue? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("Cancelled.")
        return 0
    
    # Archive current database
    print("\n[1/3] Archiving current database...")
    archive_path = search_engine.archive_and_create_new()
    print(f"  ✓ Archived to: {archive_path}")
    
    # Find all videos to re-process
    print("\n[2/3] Finding videos to re-process...")
    clips_dir = Path("./output/clips")
    
    if not clips_dir.exists():
        print("  ✗ No clips directory found. Nothing to re-index.")
        return 0
    
    # Find unique video IDs (subdirectories in clips/)
    video_dirs = [d for d in clips_dir.iterdir() if d.is_dir()]
    
    if not video_dirs:
        print("  ✗ No video directories found. Nothing to re-index.")
        return 0
    
    print(f"  Found {len(video_dirs)} video(s) to re-index:")
    for vdir in video_dirs:
        clip_count = len(list(vdir.glob("*.mp4")))
        print(f"    - {vdir.name}: {clip_count} clips")
    
    # Re-process each video
    print("\n[3/3] Re-indexing videos...")
    print("  Note: This will use existing clips and thumbnails")
    print("  Only Gemini analysis and indexing will be performed\n")
    
    pipeline = TakeOnePipeline(
        output_dir="./output",
        chroma_dir="./chroma_db"
    )
    
    total_indexed = 0
    
    for video_dir in video_dirs:
        video_id = video_dir.name
        print(f"\n  Processing: {video_id}")
        
        # Find clips for this video
        clips = sorted(video_dir.glob("*.mp4"))
        
        if not clips:
            print(f"    ✗ No clips found, skipping")
            continue
        
        # Load clip metadata from first clip's parent structure
        # We need to reconstruct clip_info dicts from existing files
        from ingestion.video_clipper import get_video_info
        
        clip_infos = []
        for i, clip_path in enumerate(clips):
            # Extract scene number from filename (scene_0001.mp4)
            scene_num = int(clip_path.stem.split('_')[1])
            
            # Get video info
            info = get_video_info(str(clip_path))
            if not info:
                continue
            
            # Find corresponding thumbnail
            thumb_path = Path("./output/thumbnails") / video_id / f"scene_{scene_num:04d}.jpg"
            
            clip_info = {
                'clip_index': scene_num,
                'clip_path': str(clip_path.absolute()),
                'clip_filename': clip_path.name,
                'thumbnail_path': str(thumb_path.absolute()) if thumb_path.exists() else None,
                'thumbnail_filename': thumb_path.name if thumb_path.exists() else None,
                'start_time': 0,  # Unknown from existing clips
                'end_time': info['duration'],
                'duration': info['duration'],
                'video_id': video_id,
                'source_video': 'unknown'
            }
            clip_infos.append(clip_info)
        
        print(f"    Found {len(clip_infos)} clips with metadata")
        
        # Analyze with Gemini (using thumbnails)
        print(f"    Analyzing with Gemini...")
        
        gemini_clips = []
        for clip in clip_infos:
            gemini_clip = clip.copy()
            if clip.get('thumbnail_path') and Path(clip['thumbnail_path']).exists():
                gemini_clip['clip_path'] = clip['thumbnail_path']
                gemini_clip['is_thumbnail'] = True
                gemini_clips.append(gemini_clip)
        
        if not gemini_clips:
            print(f"    ✗ No thumbnails found, skipping")
            continue
        
        analysis_results = pipeline.analyzer.analyze_clips_batch(gemini_clips)
        
        # Restore original clip paths
        for result in analysis_results:
            if result.get('status') == 'success' and result.get('clip_info'):
                clip_index = result['clip_info'].get('clip_index')
                original_clip = next((c for c in clip_infos if c.get('clip_index') == clip_index), None)
                if original_clip:
                    result['clip_info']['clip_path'] = original_clip['clip_path']
        
        success_count = sum(1 for r in analysis_results if r['status'] == 'success')
        print(f"    Analyzed: {success_count}/{len(gemini_clips)} successful")
        
        # Index scenes
        if analysis_results:
            indexed = pipeline.search_engine.index_scenes(analysis_results)
            total_indexed += indexed
            print(f"    Indexed: {indexed} scenes")
    
    # Final stats
    print("\n" + "="*60)
    print("RE-INDEXING COMPLETE")
    print("="*60)
    print(f"Total scenes indexed: {total_indexed}")
    
    new_stats = search_engine.get_stats()
    print(f"\nNew database:")
    print(f"  Total scenes: {new_stats['total_scenes']}")
    print(f"  Unique videos: {new_stats['unique_videos']}")
    
    print(f"\nArchive location: {archive_path}")
    print("You can restore the old database from the Streamlit UI if needed.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
