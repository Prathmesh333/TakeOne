"""
Scene Detector - Automatically detects scene boundaries in videos
Uses PySceneDetect with ContentDetector algorithm or YOLO-based semantic detection
"""

from scenedetect import detect, ContentDetector
from typing import List, Tuple, Optional, Dict
from pathlib import Path
import logging
import cv2
import numpy as np

logger = logging.getLogger(__name__)


def detect_scenes(
    video_path: str,
    threshold: float = 27.0,
    min_scene_len: float = 2.0
) -> List[Tuple[float, float]]:
    """
    Detect scene boundaries in a video.
    
    Args:
        video_path: Path to the video file
        threshold: Detection sensitivity (lower = more scenes detected)
        min_scene_len: Minimum scene length in seconds
        
    Returns:
        List of (start_time, end_time) tuples in seconds
    """
    video_path = Path(video_path)
    
    if not video_path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")
    
    logger.info(f"Detecting scenes in: {video_path.name}")
    
    # Convert min_scene_len to frames (assuming ~30fps)
    min_scene_frames = int(min_scene_len * 30)
    
    # Detect scenes using ContentDetector
    scenes = detect(
        str(video_path),
        ContentDetector(threshold=threshold, min_scene_len=min_scene_frames)
    )
    
    # Convert to (start, end) tuples in seconds
    scene_list = []
    for scene in scenes:
        start_time = scene[0].get_seconds()
        end_time = scene[1].get_seconds()
        scene_list.append((start_time, end_time))
    
    logger.info(f"Detected {len(scene_list)} scenes")
    return scene_list


def detect_scenes_with_details(
    video_path: str,
    threshold: float = 27.0
) -> List[dict]:
    """
    Detect scenes and return detailed information.
    
    Args:
        video_path: Path to video file
        threshold: Detection sensitivity
        
    Returns:
        List of dicts with scene info
    """
    scenes = detect(str(video_path), ContentDetector(threshold=threshold))
    
    scene_details = []
    for i, scene in enumerate(scenes):
        scene_details.append({
            'index': i,
            'start_time': scene[0].get_seconds(),
            'end_time': scene[1].get_seconds(),
            'duration': scene[1].get_seconds() - scene[0].get_seconds(),
            'start_frame': scene[0].get_frames(),
            'end_frame': scene[1].get_frames()
        })
    
    return scene_details


def smart_split_scenes(
    scenes: List[Tuple[float, float]],
    max_duration: float = 10.0,
    min_duration: float = 2.0
) -> List[Tuple[float, float]]:
    """
    Apply smart splitting rules to optimize scene durations.
    
    Rules:
    - Subdivide scenes longer than max_duration into smaller chunks
    - Merge scenes shorter than min_duration with adjacent scenes
    
    Args:
        scenes: List of (start, end) tuples
        max_duration: Maximum allowed scene duration before splitting
        min_duration: Minimum allowed scene duration before merging
        
    Returns:
        Optimized list of (start, end) tuples
    """
    if not scenes:
        return []
    
    optimized = []
    
    for start, end in scenes:
        duration = end - start
        
        if duration > max_duration:
            # Subdivide into smaller chunks
            current = start
            while current < end:
                chunk_end = min(current + max_duration, end)
                remaining = chunk_end - current
                
                # Only add if chunk is meaningful
                if remaining >= min_duration / 2:
                    optimized.append((current, chunk_end))
                elif optimized:
                    # Merge tiny remainder with previous
                    prev_start, _ = optimized.pop()
                    optimized.append((prev_start, chunk_end))
                
                current = chunk_end
                
        elif duration < min_duration and optimized:
            # Merge with previous scene
            prev_start, _ = optimized.pop()
            optimized.append((prev_start, end))
        else:
            optimized.append((start, end))
    
    return optimized


def get_scene_stats(scenes: List[Tuple[float, float]]) -> dict:
    """
    Get statistics about detected scenes.
    
    Args:
        scenes: List of (start, end) tuples
        
    Returns:
        Dict with scene statistics
    """
    if not scenes:
        return {
            'count': 0,
            'total_duration': 0,
            'avg_duration': 0,
            'min_duration': 0,
            'max_duration': 0
        }
    
    durations = [end - start for start, end in scenes]
    
    return {
        'count': len(scenes),
        'total_duration': sum(durations),
        'avg_duration': sum(durations) / len(durations),
        'min_duration': min(durations),
        'max_duration': max(durations)
    }


def detect_scenes_yolo(
    video_path: str,
    threshold: float = 0.4,
    min_scene_len: float = 2.0,
    sample_rate: int = 5,
    use_gpu: bool = True
) -> List[Tuple[float, float]]:
    """
    Detect scene boundaries using YOLO semantic analysis.
    Much faster than PySceneDetect and semantically aware.
    
    Args:
        video_path: Path to the video file
        threshold: Semantic change threshold (0-1, lower = more scenes)
        min_scene_len: Minimum scene length in seconds
        sample_rate: Process every Nth frame (higher = faster but less accurate)
        use_gpu: Whether to use GPU acceleration (default: True)
        
    Returns:
        List of (start_time, end_time) tuples in seconds
    """
    try:
        from ultralytics import YOLO
        import torch
    except ImportError:
        logger.error("Ultralytics not installed. Falling back to PySceneDetect.")
        return detect_scenes(video_path, min_scene_len=min_scene_len)
    
    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")
    
    logger.info(f"Detecting scenes with YOLO in: {video_path.name}")
    
    # Load YOLO model (nano for speed)
    model = YOLO("yolov8n.pt")
    
    # Enable GPU if available and requested
    if use_gpu and torch.cuda.is_available():
        model.to('cuda')
        logger.info("✅ YOLO scene detection using GPU (CUDA)")
    elif use_gpu:
        logger.warning("⚠️ GPU requested but CUDA not available, using CPU")
    else:
        logger.info("YOLO scene detection using CPU")
    
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    min_scene_frames = int(min_scene_len * fps)
    
    scene_boundaries = [0]  # Start with first frame
    prev_signature = None
    frames_since_cut = 0
    frame_idx = 0
    
    logger.info(f"Processing video at {fps:.1f} fps, sampling every {sample_rate} frames")
    logger.info(f"Total frames to process: {total_frames} (will sample ~{total_frames // sample_rate} frames)")
    
    # Progress tracking
    last_progress_log = 0
    progress_interval = 10  # Log every 10%
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Log progress
        progress = (frame_idx / total_frames) * 100
        if progress - last_progress_log >= progress_interval:
            logger.info(f"Progress: {progress:.0f}% ({frame_idx}/{total_frames} frames, {len(scene_boundaries)} scenes detected)")
            last_progress_log = progress
        
        # Sample frames for efficiency
        if frame_idx % sample_rate != 0:
            frame_idx += 1
            frames_since_cut += 1
            continue
        
        # Get YOLO detections
        results = model(frame, verbose=False)
        
        # Create semantic signature from detections
        signature = _create_semantic_signature(results[0])
        
        if prev_signature is not None:
            # Calculate semantic similarity
            similarity = _calculate_signature_similarity(prev_signature, signature)
            
            # Detect scene change
            if similarity < (1 - threshold) and frames_since_cut >= min_scene_frames:
                scene_boundaries.append(frame_idx)
                frames_since_cut = 0
                logger.debug(f"Scene boundary at frame {frame_idx} (similarity: {similarity:.3f})")
        
        prev_signature = signature
        frame_idx += 1
        frames_since_cut += 1
    
    cap.release()
    
    logger.info(f"✅ Video processing complete: {frame_idx} frames analyzed")
    
    # Add final boundary
    if scene_boundaries[-1] != total_frames - 1:
        scene_boundaries.append(total_frames - 1)
    
    # Convert frame indices to time ranges
    scenes = []
    for i in range(len(scene_boundaries) - 1):
        start_time = scene_boundaries[i] / fps
        end_time = scene_boundaries[i + 1] / fps
        scenes.append((start_time, end_time))
    
    logger.info(f"Detected {len(scenes)} scenes using YOLO")
    return scenes


def _create_semantic_signature(results) -> Dict:
    """
    Create a semantic signature from YOLO detection results.
    Captures what objects are present and their spatial distribution.
    """
    if not results.boxes or len(results.boxes) == 0:
        return {
            'classes': set(),
            'class_counts': {},
            'spatial_distribution': np.zeros(9),  # 3x3 grid
            'total_objects': 0
        }
    
    boxes = results.boxes
    classes = boxes.cls.cpu().numpy().astype(int)
    xyxy = boxes.xyxy.cpu().numpy()
    
    # Class information
    unique_classes = set(classes)
    class_counts = {int(c): int(np.sum(classes == c)) for c in unique_classes}
    
    # Spatial distribution (divide frame into 3x3 grid)
    img_h, img_w = results.orig_shape
    spatial_dist = np.zeros(9)
    
    for box in xyxy:
        x_center = (box[0] + box[2]) / 2
        y_center = (box[1] + box[3]) / 2
        
        grid_x = min(int(x_center / img_w * 3), 2)
        grid_y = min(int(y_center / img_h * 3), 2)
        grid_idx = grid_y * 3 + grid_x
        
        spatial_dist[grid_idx] += 1
    
    # Normalize spatial distribution
    if spatial_dist.sum() > 0:
        spatial_dist = spatial_dist / spatial_dist.sum()
    
    return {
        'classes': unique_classes,
        'class_counts': class_counts,
        'spatial_distribution': spatial_dist,
        'total_objects': len(classes)
    }


def _calculate_signature_similarity(sig1: Dict, sig2: Dict) -> float:
    """
    Calculate similarity between two semantic signatures.
    Returns value between 0 (completely different) and 1 (identical).
    """
    # Class overlap (Jaccard similarity)
    classes1 = sig1['classes']
    classes2 = sig2['classes']
    
    if len(classes1) == 0 and len(classes2) == 0:
        class_similarity = 1.0
    elif len(classes1) == 0 or len(classes2) == 0:
        class_similarity = 0.0
    else:
        intersection = len(classes1 & classes2)
        union = len(classes1 | classes2)
        class_similarity = intersection / union if union > 0 else 0.0
    
    # Spatial distribution similarity (cosine similarity)
    spatial1 = sig1['spatial_distribution']
    spatial2 = sig2['spatial_distribution']
    
    dot_product = np.dot(spatial1, spatial2)
    norm1 = np.linalg.norm(spatial1)
    norm2 = np.linalg.norm(spatial2)
    
    if norm1 > 0 and norm2 > 0:
        spatial_similarity = dot_product / (norm1 * norm2)
    else:
        spatial_similarity = 1.0 if norm1 == norm2 else 0.0
    
    # Object count similarity
    count1 = sig1['total_objects']
    count2 = sig2['total_objects']
    max_count = max(count1, count2)
    count_similarity = 1.0 - abs(count1 - count2) / max_count if max_count > 0 else 1.0
    
    # Weighted combination
    similarity = (
        class_similarity * 0.5 +      # What objects are present (most important)
        spatial_similarity * 0.3 +     # Where they are
        count_similarity * 0.2         # How many there are
    )
    
    return similarity


def detect_scenes_hybrid(
    video_path: str,
    use_yolo: bool = True,
    use_gpu: bool = True,
    **kwargs
) -> List[Tuple[float, float]]:
    """
    Detect scenes using YOLO if available, fallback to PySceneDetect.
    
    Args:
        video_path: Path to video file
        use_yolo: Whether to use YOLO (if False, uses PySceneDetect)
        use_gpu: Whether to use GPU acceleration for YOLO
        **kwargs: Additional arguments for the detection method
        
    Returns:
        List of (start_time, end_time) tuples
    """
    if use_yolo:
        try:
            return detect_scenes_yolo(video_path, use_gpu=use_gpu, **kwargs)
        except Exception as e:
            logger.warning(f"YOLO detection failed: {e}. Falling back to PySceneDetect.")
            # Remove use_gpu from kwargs for PySceneDetect
            kwargs.pop('use_gpu', None)
            return detect_scenes(video_path, **kwargs)
    else:
        # Remove use_gpu from kwargs for PySceneDetect
        kwargs.pop('use_gpu', None)
        return detect_scenes(video_path, **kwargs)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
        use_yolo = "--yolo" in sys.argv
        
        print(f"Analyzing: {video_path}")
        print(f"Method: {'YOLO' if use_yolo else 'PySceneDetect'}")
        
        # Detect scenes
        if use_yolo:
            scenes = detect_scenes_yolo(video_path)
        else:
            scenes = detect_scenes(video_path)
        
        print(f"\nFound {len(scenes)} raw scenes:")
        
        for i, (start, end) in enumerate(scenes[:10]):
            duration = end - start
            print(f"  Scene {i+1}: {start:.1f}s - {end:.1f}s ({duration:.1f}s)")
        
        if len(scenes) > 10:
            print(f"  ... and {len(scenes) - 10} more")
        
        # Apply smart splitting
        optimized = smart_split_scenes(scenes)
        print(f"\nAfter optimization: {len(optimized)} clips")
        
        # Show stats
        stats = get_scene_stats(optimized)
        print(f"\nStats:")
        print(f"  Total duration: {stats['total_duration']:.1f}s")
        print(f"  Avg scene: {stats['avg_duration']:.1f}s")
        print(f"  Range: {stats['min_duration']:.1f}s - {stats['max_duration']:.1f}s")
    else:
        print("Usage: python scene_detector.py <video_path> [--yolo]")
