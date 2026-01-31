# Ingestion module
"""
TakeOne Ingestion Pipeline

Modules:
- scene_detector: Automatic scene boundary detection
- video_clipper: FFmpeg-based clip extraction
- gemini_analyzer: Gemini 2.5 video analysis
- pipeline: Complete processing orchestrator
- embedder: CLIP embeddings (legacy)
- frame_extractor: Frame extraction utilities
- video_chunker: Fixed-duration chunking (legacy)
"""

from .scene_detector import detect_scenes, smart_split_scenes, get_scene_stats
from .video_clipper import extract_clip, extract_all_clips, extract_thumbnail, get_video_info
from .gemini_analyzer import GeminiAnalyzer, get_analyzer, analyze_clip, analyze_clips
from .pipeline import TakeOnePipeline

__all__ = [
    # Scene detection
    'detect_scenes',
    'smart_split_scenes',
    'get_scene_stats',
    
    # Video clipping
    'extract_clip',
    'extract_all_clips',
    'extract_thumbnail',
    'get_video_info',
    
    # Gemini analysis
    'GeminiAnalyzer',
    'get_analyzer',
    'analyze_clip',
    'analyze_clips',
    
    # Pipeline
    'TakeOnePipeline',
]
