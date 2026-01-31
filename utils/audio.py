"""
Audio utilities - Whisper transcription for dialogue search
"""
import os
from typing import Dict, Optional
from pathlib import Path


def extract_audio(video_path: str, output_path: Optional[str] = None) -> str:
    """
    Extract audio track from video file.
    
    Args:
        video_path: Path to video file
        output_path: Optional output path for audio file
        
    Returns:
        Path to extracted audio file
    """
    import subprocess
    
    video_path = Path(video_path)
    if output_path is None:
        output_path = video_path.with_suffix(".wav")
    
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vn",  # No video
        "-acodec", "pcm_s16le",
        "-ar", "16000",  # Whisper expects 16kHz
        "-ac", "1",  # Mono
        "-loglevel", "error",
        str(output_path)
    ]
    
    subprocess.run(cmd, check=True, capture_output=True)
    return str(output_path)


def transcribe_audio(audio_path: str, model_size: str = "base") -> Dict:
    """
    Transcribe audio using Whisper.
    
    Args:
        audio_path: Path to audio file
        model_size: Whisper model size (tiny, base, small, medium, large)
        
    Returns:
        Dictionary with transcript text and segments with timestamps
    """
    import whisper
    
    model = whisper.load_model(model_size)
    result = model.transcribe(audio_path)
    
    return {
        "text": result["text"],
        "segments": [
            {
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"]
            }
            for seg in result["segments"]
        ],
        "language": result.get("language", "en")
    }


def transcribe_video(video_path: str, model_size: str = "base") -> Dict:
    """
    Extract audio from video and transcribe.
    
    Args:
        video_path: Path to video file
        model_size: Whisper model size
        
    Returns:
        Transcription result with timestamps
    """
    import tempfile
    
    # Extract audio to temp file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        audio_path = tmp.name
    
    try:
        extract_audio(video_path, audio_path)
        return transcribe_audio(audio_path, model_size)
    finally:
        # Clean up temp file
        if os.path.exists(audio_path):
            os.remove(audio_path)


def get_dialogue_for_clip(
    full_transcript: Dict,
    start_time: float,
    end_time: float
) -> str:
    """
    Get dialogue text for a specific time range.
    
    Args:
        full_transcript: Full video transcription
        start_time: Clip start time in seconds
        end_time: Clip end time in seconds
        
    Returns:
        Dialogue text within the time range
    """
    dialogue_parts = []
    
    for segment in full_transcript.get("segments", []):
        seg_start = segment["start"]
        seg_end = segment["end"]
        
        # Check for overlap
        if seg_end >= start_time and seg_start <= end_time:
            dialogue_parts.append(segment["text"].strip())
    
    return " ".join(dialogue_parts)
