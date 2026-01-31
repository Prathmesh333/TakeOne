"""
Video Chunker - Splits videos into 2-second segments for processing
"""
import os
import subprocess
from pathlib import Path
from typing import List
import tempfile


def chunk_video(video_path: str, output_dir: str, chunk_duration: int = 2) -> List[str]:
    """
    Split a video into chunks of specified duration.
    
    Args:
        video_path: Path to input video file
        output_dir: Directory to save chunks
        chunk_duration: Duration of each chunk in seconds
        
    Returns:
        List of paths to created chunk files
    """
    video_path = Path(video_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get video duration using ffprobe
    duration = get_video_duration(video_path)
    
    chunk_paths = []
    chunk_index = 0
    
    for start_time in range(0, int(duration), chunk_duration):
        output_file = output_dir / f"{video_path.stem}_chunk_{chunk_index:04d}.mp4"
        
        # Use FFmpeg to extract chunk
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-ss", str(start_time),
            "-t", str(chunk_duration),
            "-c:v", "libx264",
            "-c:a", "aac",
            "-loglevel", "error",
            str(output_file)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            chunk_paths.append(str(output_file))
            chunk_index += 1
        except subprocess.CalledProcessError as e:
            print(f"Error creating chunk {chunk_index}: {e}")
            
    return chunk_paths


def get_video_duration(video_path: Path) -> float:
    """Get video duration in seconds using ffprobe."""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(video_path)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except (subprocess.CalledProcessError, ValueError):
        return 0.0


def get_video_metadata(video_path: str) -> dict:
    """Extract basic metadata from video file."""
    path = Path(video_path)
    return {
        "filename": path.name,
        "stem": path.stem,
        "duration": get_video_duration(path),
        "path": str(path.absolute())
    }
