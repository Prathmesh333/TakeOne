"""
Together AI Analyzer - Fast and cheap alternative to Gemini
Uses Llama 3.2 Vision or Qwen2-VL for video scene understanding
Much faster than Gemini free tier (60+ RPM vs 5 RPM)
"""

import os
import json
import time
import base64
from pathlib import Path
from typing import List, Dict, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

try:
    from together import Together
    TOGETHER_AVAILABLE = True
except ImportError:
    TOGETHER_AVAILABLE = False
    logger.warning("Together AI not installed. Run: pip install together")


class TogetherAnalyzer:
    """Together AI vision analyzer for scene understanding."""
    
    # Default analysis prompt (same as Gemini for consistency)
    DEFAULT_PROMPT = """Analyze this image from a video for a film search engine.

Provide a JSON response with these exact fields:
{
    "scene_type": "one of: action, dialogue, romance, chase, fight, comedy, drama, transition, establishing, montage, emotional, suspense",
    "description": "2-3 sentences describing what happens in this scene, focusing on visual content",
    "characters": ["list of visible people/characters with brief physical descriptions"],
    "setting": "location and environment description",
    "mood": "emotional tone (e.g., tense, joyful, melancholic, peaceful, dramatic, mysterious)",
    "lighting": "lighting style (e.g., high-key, low-key, natural, dramatic, silhouette, neon)",
    "camera_work": "shot types and movements (e.g., close-up, wide shot, tracking, handheld, dolly)",
    "key_actions": ["important actions or events that occur"],
    "objects": ["notable objects visible in the scene"],
    "colors": ["dominant colors in the scene"],
    "audio_hint": "description of likely audio/music mood if applicable, or null",
    "tags": ["15-20 searchable keywords for this scene, be comprehensive"]
}

IMPORTANT: Respond with ONLY valid JSON. No markdown, no explanation, just the JSON object."""

    DEFAULT_PROMPT_WITH_YOLO = """Analyze this image from a video for a film search engine.

YOLO Pre-Analysis Context:
{yolo_context}

Use this context to enhance your analysis, but verify and expand upon it with your own visual understanding.

Provide a JSON response with these exact fields:
{
    "scene_type": "one of: action, dialogue, romance, chase, fight, comedy, drama, transition, establishing, montage, emotional, suspense",
    "description": "2-3 sentences describing what happens in this scene, focusing on visual content",
    "characters": ["list of visible people/characters with brief physical descriptions"],
    "setting": "location and environment description",
    "mood": "emotional tone (e.g., tense, joyful, melancholic, peaceful, dramatic, mysterious)",
    "lighting": "lighting style (e.g., high-key, low-key, natural, dramatic, silhouette, neon)",
    "camera_work": "shot types and movements (e.g., close-up, wide shot, tracking, handheld, dolly)",
    "key_actions": ["important actions or events that occur"],
    "objects": ["notable objects visible in the scene"],
    "colors": ["dominant colors in the scene"],
    "audio_hint": "description of likely audio/music mood if applicable, or null",
    "tags": ["15-20 searchable keywords for this scene, be comprehensive"]
}

IMPORTANT: Respond with ONLY valid JSON. No markdown, no explanation, just the JSON object."""

    def __init__(
        self,
        model_name: str = "meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
        max_concurrent: int = 10,
        request_delay: float = 0.1,
        api_key: Optional[str] = None
    ):
        """
        Initialize Together AI analyzer.
        
        Args:
            model_name: Model to use (default: Llama 3.2 Vision)
                       Options: 
                       - meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo (fast, good)
                       - meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo (best quality, slower)
                       - Qwen/Qwen2-VL-72B-Instruct (excellent quality)
            max_concurrent: Maximum concurrent API requests
            request_delay: Delay between requests (Together has high limits)
            api_key: Together API key (uses TOGETHER_API_KEY env var if not provided)
        """
        if not TOGETHER_AVAILABLE:
            raise ImportError("Together AI not installed. Run: pip install together")
        
        self.api_key = api_key or os.environ.get("TOGETHER_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "Together API key not found. Set TOGETHER_API_KEY environment variable "
                "or pass api_key parameter. Get key at: https://together.ai"
            )
        
        self.client = Together(api_key=self.api_key)
        self.model_name = model_name
        self.max_concurrent = max_concurrent
        self.request_delay = request_delay
        self.prompt = self.DEFAULT_PROMPT
        
        logger.info(f"Initialized Together AI analyzer with model: {model_name}")
        logger.info(f"  Max concurrent: {max_concurrent} (much faster than Gemini!)")
    
    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64."""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')
    
    def analyze_image(self, image_path: str, retries: int = 3, yolo_context: Optional[Dict] = None) -> Dict:
        """
        Analyze a single image using Together AI.
        
        Args:
            image_path: Path to the image file
            retries: Number of retry attempts
            yolo_context: Optional YOLO detection context
            
        Returns:
            Analysis result dict
        """
        image_path = Path(image_path)
        
        if not image_path.exists():
            return {
                "status": "error",
                "clip_path": str(image_path),
                "error": f"File not found: {image_path}"
            }
        
        # Select prompt based on YOLO context
        if yolo_context and yolo_context.get('objects_detected'):
            prompt = self.DEFAULT_PROMPT_WITH_YOLO.format(
                yolo_context=f"Detected objects: {', '.join(yolo_context['objects_detected'])} ({yolo_context['num_objects']} total objects)"
            )
        else:
            prompt = self.prompt
        
        for attempt in range(retries):
            try:
                # Encode image
                image_base64 = self._encode_image(str(image_path))
                
                # Call Together AI
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{image_base64}"
                                    }
                                }
                            ]
                        }
                    ],
                    temperature=0.3,
                    max_tokens=2048
                )
                
                # Parse response
                json_text = response.choices[0].message.content.strip()
                
                # Clean up formatting
                if json_text.startswith("```json"):
                    json_text = json_text[7:]
                if json_text.startswith("```"):
                    json_text = json_text[3:]
                if json_text.endswith("```"):
                    json_text = json_text[:-3]
                json_text = json_text.strip()
                
                analysis = json.loads(json_text)
                
                return {
                    "status": "success",
                    "clip_path": str(image_path),
                    "analysis": analysis,
                    "yolo_enhanced": bool(yolo_context)
                }
                
            except Exception as e:
                logger.warning(f"Analysis error on attempt {attempt + 1}: {e}")
                if attempt < retries - 1:
                    time.sleep(1)
                    continue
                return {
                    "status": "error",
                    "clip_path": str(image_path),
                    "error": str(e)
                }
    
    def analyze_clip(self, clip_path: str, retries: int = 3, yolo_context: Optional[Dict] = None) -> Dict:
        """
        Analyze a video clip or image.
        For videos, extracts middle frame and analyzes it.
        
        Args:
            clip_path: Path to the video clip or image
            retries: Number of retry attempts
            yolo_context: Optional YOLO detection context
            
        Returns:
            Analysis result dict
        """
        clip_path = Path(clip_path)
        
        # If it's an image, analyze directly
        if clip_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
            return self.analyze_image(str(clip_path), retries, yolo_context)
        
        # For videos, extract middle frame
        # (Together AI doesn't support video directly, so we use thumbnails)
        # Your pipeline already generates thumbnails, so this should work
        logger.warning(f"Video analysis not directly supported. Use thumbnail instead: {clip_path}")
        return {
            "status": "error",
            "clip_path": str(clip_path),
            "error": "Video analysis not supported. Use thumbnail/image instead."
        }
    
    def analyze_clips_batch(
        self,
        clips: List[Dict],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[Dict]:
        """
        Analyze multiple clips with parallel processing.
        Much faster than Gemini (60+ RPM vs 5 RPM).
        
        Args:
            clips: List of clip info dicts (must have 'clip_path' key)
            progress_callback: Optional callback(current, total) for progress updates
            
        Returns:
            List of analysis results
        """
        results = []
        total = len(clips)
        completed = 0
        
        logger.info(f"Starting batch analysis of {total} clips with Together AI")
        logger.info(f"  Expected time: ~{total / 60:.1f} minutes (vs ~{total / 5:.1f} min with Gemini)")
        
        # Check YOLO context
        yolo_enhanced_count = sum(1 for c in clips if c.get('yolo_context'))
        if yolo_enhanced_count > 0:
            logger.info(f"  {yolo_enhanced_count} clips have YOLO context")
        
        with ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
            # Submit tasks
            futures = {}
            for i, clip in enumerate(clips):
                yolo_context = clip.get('yolo_context')
                future = executor.submit(self.analyze_clip, clip['clip_path'], yolo_context=yolo_context)
                futures[future] = clip
                
                # Minimal rate limiting
                if (i + 1) % self.max_concurrent == 0 and i + 1 < total:
                    time.sleep(self.request_delay)
            
            # Collect results
            for future in as_completed(futures):
                clip_info = futures[future]
                try:
                    result = future.result()
                    result['clip_info'] = clip_info
                    results.append(result)
                except Exception as e:
                    results.append({
                        "status": "error",
                        "clip_info": clip_info,
                        "clip_path": clip_info.get('clip_path'),
                        "error": str(e)
                    })
                
                completed += 1
                if progress_callback:
                    progress_callback(completed, total)
        
        # Sort by original order
        results.sort(key=lambda x: x.get('clip_info', {}).get('clip_index', 0))
        
        success_count = sum(1 for r in results if r['status'] == 'success')
        yolo_enhanced = sum(1 for r in results if r.get('yolo_enhanced'))
        
        logger.info(f"Batch analysis complete: {success_count}/{total} successful")
        if yolo_enhanced > 0:
            logger.info(f"  {yolo_enhanced} analyses enhanced with YOLO context")
        
        return results


# Convenience functions
_analyzer: Optional[TogetherAnalyzer] = None


def get_analyzer(model_name: str = "meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo") -> TogetherAnalyzer:
    """Get or create global analyzer instance."""
    global _analyzer
    if _analyzer is None:
        _analyzer = TogetherAnalyzer(model_name=model_name)
    return _analyzer


def analyze_clip(clip_path: str) -> Dict:
    """Convenience function to analyze a single clip."""
    return get_analyzer().analyze_clip(clip_path)


def analyze_clips(
    clips: List[Dict],
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> List[Dict]:
    """Convenience function to analyze multiple clips."""
    return get_analyzer().analyze_clips_batch(clips, progress_callback)


if __name__ == "__main__":
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        print(f"Analyzing: {image_path}")
        
        try:
            result = analyze_clip(image_path)
            
            if result['status'] == 'success':
                print("\n Analysis successful!")
                print(json.dumps(result['analysis'], indent=2))
            else:
                print(f"\n Error: {result['error']}")
                
        except ValueError as e:
            print(f"\nConfiguration error: {e}")
            print("Get API key at: https://together.ai")
            print("Set TOGETHER_API_KEY in your environment or .env file")
    else:
        print("Usage: python together_analyzer.py <image_path>")
        print("\nGet API key at: https://together.ai ($5 free credit)")
        print("Set TOGETHER_API_KEY environment variable")
