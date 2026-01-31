"""
Frame Extractor - Extracts representative frames from video chunks
"""
import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple
from PIL import Image


def extract_frames(video_path: str, sample_rate: int = 1) -> List[Image.Image]:
    """
    Extract frames from a video at specified sample rate.
    
    Args:
        video_path: Path to video file
        sample_rate: Extract 1 frame every N seconds (default: 1)
        
    Returns:
        List of PIL Image objects
    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps * sample_rate)
    
    frames = []
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        if frame_count % frame_interval == 0:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            frames.append(pil_image)
            
        frame_count += 1
    
    cap.release()
    return frames


def extract_keyframe(video_path: str) -> Image.Image:
    """
    Extract a single representative keyframe from video.
    Uses the middle frame as the keyframe.
    
    Args:
        video_path: Path to video file
        
    Returns:
        PIL Image of the keyframe
    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    middle_frame = total_frames // 2
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        raise ValueError(f"Could not read frame from: {video_path}")
    
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb_frame)


def create_thumbnail(video_path: str, size: Tuple[int, int] = (320, 180)) -> Image.Image:
    """Create a thumbnail from video's keyframe."""
    keyframe = extract_keyframe(video_path)
    keyframe.thumbnail(size, Image.Resampling.LANCZOS)
    return keyframe


def save_thumbnail(video_path: str, output_path: str, size: Tuple[int, int] = (320, 180)) -> str:
    """Save thumbnail to file and return path."""
    thumbnail = create_thumbnail(video_path, size)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    thumbnail.save(output_path, "JPEG", quality=85)
    return str(output_path)
