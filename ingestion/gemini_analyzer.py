"""
Gemini Analyzer - Uses Gemini 2.5 Pro for video scene understanding
Provides rich semantic analysis of video clips for search indexing
"""

import google.generativeai as genai
import os
import json
import time
from pathlib import Path
from typing import List, Dict, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class GeminiAnalyzer:
    """Gemini 2.5 Pro video analyzer for scene understanding."""
    
    # Default/Standard analysis prompt (simpler, faster, more reliable)
    DEFAULT_PROMPT = """Analyze this image from a video for a film search engine.

Provide a JSON response with these fields:

scene_type: one of (action, dialogue, romance, chase, fight, comedy, drama, transition, establishing, montage)
description: 3-4 sentences describing what's happening, who's present, their actions, expressions, and the setting
mood: primary emotional tone (e.g., tense, joyful, melancholic, dramatic, peaceful, suspenseful)
setting: detailed description of location, time of day, indoor/outdoor, environment
lighting: description of lighting (e.g., natural daylight, dramatic shadows, soft indoor, golden hour, harsh fluorescent)
camera_work: shot type and angle (e.g., close-up, wide shot, medium shot, low angle, high angle, eye-level)
colors: list of 3-5 dominant colors
people: list with brief description of each person visible
objects: list of significant objects visible
actions: list of actions happening
tags: comprehensive list of 15-20 searchable keywords

Return ONLY a valid JSON object with these exact field names. No explanation, no markdown, just the JSON."""

    DEFAULT_PROMPT_WITH_YOLO = """Analyze this image from a video for a film search engine.

YOLO Pre-Analysis Context:
{yolo_context}

Use this as a starting point, but add more detail through your visual analysis.

Provide a JSON response with these fields:

scene_type: one of (action, dialogue, romance, chase, fight, comedy, drama, transition, establishing, montage)
description: 2-3 sentences describing what's happening in the scene
mood: primary emotional tone (e.g., tense, joyful, melancholic, dramatic, peaceful)
setting: brief description of location and time of day
lighting: brief description of lighting (e.g., natural daylight, dramatic shadows, soft indoor)
camera_work: shot type and angle (e.g., close-up, wide shot, low angle)
colors: list of dominant colors
tags: searchable keywords for this scene

Return ONLY a valid JSON object. No markdown, no explanation, just the JSON object."""
    
    # Enhanced analysis prompt with NER and detailed extraction
    # Optimized for Gemini's native JSON mode
    ENHANCED_PROMPT = """Analyze this image frame from a video for a comprehensive search engine.

Provide detailed analysis in the following JSON structure. Be thorough but concise.

{
    "scene_type": "one of: action, dialogue, romance, chase, fight, comedy, drama, transition, establishing, montage",
    
    "description": "3-4 sentences: what's happening, who's present, actions, expressions, setting",
    
    "detailed_description": "6-8 sentences covering: foreground, background, people, objects, actions, expressions, spatial layout",
    
    "entities": {
        "people": ["brief description of each person visible"],
        "locations": ["specific places/settings"],
        "organizations": ["brands, logos, company names visible"],
        "objects": ["significant objects with brief details"],
        "vehicles": ["vehicles with type and color"],
        "animals": ["animals with species"],
        "text_visible": ["any text, signs, labels visible"]
    },
    
    "people_analysis": [
        {
            "person_id": 1,
            "description": "physical description",
            "clothing": "clothing with colors",
            "position": "location in frame",
            "action": "what they're doing",
            "expression": "facial expression",
            "body_language": "posture, gestures"
        }
    ],
    
    "setting": {
        "location_type": "indoor/outdoor/vehicle",
        "specific_location": "description of place",
        "time_of_day": "morning/afternoon/evening/night",
        "weather": "if outdoor, weather conditions"
    },
    
    "mood": "primary emotional tone",
    "secondary_moods": ["additional emotional tones"],
    
    "lighting": {
        "type": "natural/artificial/mixed",
        "quality": "harsh/soft/dramatic/flat",
        "direction": "front/back/side/top"
    },
    
    "colors": {
        "dominant": ["3-5 most prominent colors"],
        "accent": ["notable accent colors"]
    },
    
    "camera_work": {
        "shot_type": "close-up/medium/long/extreme long",
        "angle": "eye-level/high-angle/low-angle",
        "focus": "what's in sharp focus"
    },
    
    "actions": ["every action happening"],
    "interactions": ["how people/objects interact"],
    
    "search_keywords": ["25-35 comprehensive keywords: actions, objects, people, emotions, setting, colors"],
    
    "searchable_phrases": ["8-10 natural phrases someone might search for"]
}

Return ONLY the JSON object with no additional text."""

    ENHANCED_PROMPT_WITH_YOLO = """Analyze this image frame from a video for a comprehensive search engine.

YOLO Pre-Analysis Context:
{yolo_context}

Use this as a starting point, but provide MORE detail through your visual analysis.

Provide detailed analysis in the following JSON structure. Be thorough but concise.

{
    "scene_type": "one of: action, dialogue, romance, chase, fight, comedy, drama, transition, establishing, montage",
    
    "description": "3-4 sentences: what's happening, who's present, actions, expressions, setting",
    
    "detailed_description": "6-8 sentences covering: foreground, background, people, objects, actions, expressions, spatial layout",
    
    "entities": {
        "people": ["brief description of each person visible"],
        "locations": ["specific places/settings"],
        "organizations": ["brands, logos, company names visible"],
        "objects": ["significant objects with brief details"],
        "vehicles": ["vehicles with type and color"],
        "animals": ["animals with species"],
        "text_visible": ["any text, signs, labels visible"]
    },
    
    "people_analysis": [
        {
            "person_id": 1,
            "description": "physical description",
            "clothing": "clothing with colors",
            "position": "location in frame",
            "action": "what they're doing",
            "expression": "facial expression",
            "body_language": "posture, gestures"
        }
    ],
    
    "setting": {
        "location_type": "indoor/outdoor/vehicle",
        "specific_location": "description of place",
        "time_of_day": "morning/afternoon/evening/night",
        "weather": "if outdoor, weather conditions"
    },
    
    "mood": "primary emotional tone",
    "secondary_moods": ["additional emotional tones"],
    
    "lighting": {
        "type": "natural/artificial/mixed",
        "quality": "harsh/soft/dramatic/flat",
        "direction": "front/back/side/top"
    },
    
    "colors": {
        "dominant": ["3-5 most prominent colors"],
        "accent": ["notable accent colors"]
    },
    
    "camera_work": {
        "shot_type": "close-up/medium/long/extreme long",
        "angle": "eye-level/high-angle/low-angle",
        "focus": "what's in sharp focus"
    },
    
    "actions": ["every action happening"],
    "interactions": ["how people/objects interact"],
    
    "search_keywords": ["25-35 comprehensive keywords: actions, objects, people, emotions, setting, colors"],
    
    "searchable_phrases": ["8-10 natural phrases someone might search for"]
}

Return ONLY the JSON object with no additional text."""

    def __init__(
        self,
        model_name: str = "gemini-2.5-flash",
        max_concurrent: int = None,  # No limit - process all at once
        request_delay: float = 0.0,  # No artificial delays
        api_key: Optional[str] = None,
        use_enhanced_prompt: bool = False  # Keep simple prompt for reliability
    ):
        """
        Initialize Gemini analyzer.
        
        Args:
            model_name: Gemini model to use (gemini-2.5-pro, gemini-2.5-flash, etc.)
            max_concurrent: Deprecated - no longer used (API handles rate limiting)
            request_delay: Deprecated - no longer used (API handles rate limiting)
            api_key: Gemini API key (uses GEMINI_API_KEY env var if not provided)
            use_enhanced_prompt: Use enhanced prompt with NER and detailed analysis (default: False)
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "Gemini API key not found. Set GEMINI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        genai.configure(api_key=self.api_key)
        
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        self.max_concurrent = max_concurrent  # Kept for backwards compatibility but not used
        self.request_delay = request_delay  # Kept for backwards compatibility but not used
        self.use_enhanced_prompt = use_enhanced_prompt
        self.prompt = self.ENHANCED_PROMPT if use_enhanced_prompt else self.DEFAULT_PROMPT
        
        logger.info(f"Initialized Gemini analyzer with model: {model_name}")
        if use_enhanced_prompt:
            logger.info("  Using ENHANCED prompt with NER and detailed analysis")
        else:
            logger.info("  Using standard prompt (faster, simpler, more reliable)")
        logger.info("  No artificial rate limiting - API handles concurrency")
    
    def set_prompt(self, prompt: str):
        """Set a custom analysis prompt."""
        self.prompt = prompt
    
    def analyze_image(self, image_path: str, retries: int = 3, yolo_context: Optional[Dict] = None) -> Dict:
        """
        Analyze a single image frame using Gemini.
        
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
                "clip_path": str(image_path), # Use 'clip_path' key for compatibility
                "error": f"File not found: {image_path}"
            }
            
        # Select appropriate prompt based on context and settings
        if yolo_context and yolo_context.get('objects_detected'):
            if self.use_enhanced_prompt:
                prompt = self.ENHANCED_PROMPT_WITH_YOLO.format(
                    yolo_context=f"Detected objects: {', '.join(yolo_context['objects_detected'])} ({yolo_context['num_objects']} total objects)"
                )
            else:
                prompt = self.DEFAULT_PROMPT_WITH_YOLO.format(
                    yolo_context=f"Detected objects: {', '.join(yolo_context['objects_detected'])} ({yolo_context['num_objects']} total objects)"
                )
        else:
            prompt = self.prompt
        
        # Adapt for image analysis
        prompt = prompt.replace("video clip", "image frame").replace("this video", "this image")

        for attempt in range(retries):
            img_file = None
            try:
                # Upload/Load image
                logger.debug(f"Analyzing image with {'ENHANCED' if self.use_enhanced_prompt else 'standard'} prompt: {image_path.name}")
                
                img_file = genai.upload_file(str(image_path))
                
                # Wait for file to be ready (important for reliability)
                max_wait = 30
                waited = 0
                while img_file.state.name == "PROCESSING" and waited < max_wait:
                    time.sleep(1)
                    waited += 1
                    img_file = genai.get_file(img_file.name)
                
                if img_file.state.name == "FAILED":
                    raise Exception(f"Image upload failed: {img_file.state.name}")
                
                if img_file.state.name == "PROCESSING":
                    raise Exception(f"Image upload timed out after {max_wait}s")
                
                logger.debug(f"Image uploaded and ready: {image_path.name}")
                
                # Generate analysis with Gemini's native JSON mode
                # This guarantees valid JSON output with no truncation
                max_tokens = 4096 if self.use_enhanced_prompt else 2048
                
                response = self.model.generate_content(
                    [prompt, img_file],
                    generation_config={
                        "temperature": 0.3,
                        "max_output_tokens": max_tokens,
                        "response_mime_type": "application/json"  # Native JSON mode
                    }
                )
                
                # Parse JSON response - should be clean with JSON mode
                json_text = response.text.strip()
                
                # JSON mode should return clean JSON, but handle edge cases
                if json_text.startswith("```json"):
                    json_text = json_text[7:]
                elif json_text.startswith("```"):
                    json_text = json_text[3:]
                if json_text.endswith("```"):
                    json_text = json_text[:-3]
                json_text = json_text.strip()
                
                # Parse JSON with robust error handling
                try:
                    analysis = json.loads(json_text)
                    logger.debug(f"Successfully parsed JSON response (JSON mode)")
                except json.JSONDecodeError as e:
                    # JSON mode should prevent this, but Gemini sometimes returns malformed JSON
                    logger.warning(f"JSON parse error even with JSON mode: {e}")
                    
                    # Try to repair the JSON by fixing common issues
                    import re
                    
                    # Strategy: Only escape newlines/tabs that are INSIDE string values
                    # This is complex, so we'll use a simpler approach:
                    # Try to find and complete the JSON object
                    
                    json_text_fixed = json_text
                    
                    # Fix 1: Remove trailing commas before closing braces/brackets
                    json_text_fixed = re.sub(r',(\s*[}\]])', r'\1', json_text_fixed)
                    
                    # Fix 2: Try to find the last complete JSON object
                    # Count braces to find where the JSON might be truncated
                    try:
                        # First try with just trailing comma fix
                        analysis = json.loads(json_text_fixed)
                        logger.debug(f"Successfully parsed JSON after removing trailing commas")
                    except json.JSONDecodeError as e2:
                        # Try to extract valid JSON portion if truncated
                        try:
                            depth = 0
                            last_valid_pos = 0
                            in_string = False
                            escape_next = False
                            
                            for i, char in enumerate(json_text_fixed):
                                if escape_next:
                                    escape_next = False
                                    continue
                                
                                if char == '\\':
                                    escape_next = True
                                    continue
                                
                                if char == '"' and not escape_next:
                                    in_string = not in_string
                                
                                if not in_string:
                                    if char == '{' or char == '[':
                                        depth += 1
                                    elif char == '}' or char == ']':
                                        depth -= 1
                                        if depth == 0:
                                            last_valid_pos = i + 1
                            
                            if last_valid_pos > 0:
                                json_text_fixed = json_text_fixed[:last_valid_pos]
                                analysis = json.loads(json_text_fixed)
                                logger.debug(f"Successfully parsed truncated JSON")
                            else:
                                # Last resort: try to close the JSON manually
                                # Count open braces/brackets and close them
                                open_braces = json_text_fixed.count('{') - json_text_fixed.count('}')
                                open_brackets = json_text_fixed.count('[') - json_text_fixed.count(']')
                                
                                # Remove any incomplete string at the end
                                if json_text_fixed.count('"') % 2 != 0:
                                    # Odd number of quotes - incomplete string
                                    last_quote = json_text_fixed.rfind('"')
                                    if last_quote > 0:
                                        # Find the comma or brace before this incomplete string
                                        search_pos = last_quote - 1
                                        while search_pos > 0 and json_text_fixed[search_pos] not in [',', '{', '[']:
                                            search_pos -= 1
                                        if json_text_fixed[search_pos] == ',':
                                            json_text_fixed = json_text_fixed[:search_pos]
                                        else:
                                            json_text_fixed = json_text_fixed[:last_quote]
                                
                                # Close the JSON
                                json_text_fixed += ']' * open_brackets
                                json_text_fixed += '}' * open_braces
                                
                                analysis = json.loads(json_text_fixed)
                                logger.debug(f"Successfully parsed JSON after manual closure")
                        except Exception as e3:
                            # All repair attempts failed
                            logger.error(f"JSON repair failed. Original error: {e}")
                            raise e
                
                # CRITICAL FIX: Clean up malformed keys with embedded newlines/whitespace
                # Sometimes Gemini returns keys like "\n    \"scene_type\"" instead of "scene_type"
                def clean_dict_keys(obj):
                    """Recursively clean dictionary keys by removing newlines and extra whitespace."""
                    if isinstance(obj, dict):
                        cleaned = {}
                        for key, value in obj.items():
                            # Clean the key: remove newlines, tabs, and extra spaces
                            clean_key = key.replace('\n', '').replace('\t', '').replace('"', '').strip()
                            cleaned[clean_key] = clean_dict_keys(value)
                        return cleaned
                    elif isinstance(obj, list):
                        return [clean_dict_keys(item) for item in obj]
                    else:
                        return obj
                
                analysis = clean_dict_keys(analysis)
                
                # Clean up uploaded file
                if img_file:
                    try:
                        genai.delete_file(img_file.name)
                        logger.debug(f"Cleaned up uploaded file: {image_path.name}")
                    except Exception as cleanup_error:
                        logger.warning(f"Failed to cleanup file: {cleanup_error}")
                
                return {
                    "status": "success",
                    "clip_path": str(image_path),
                    "analysis": analysis,
                    "yolo_enhanced": bool(yolo_context)
                }
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error on attempt {attempt + 1}/{retries} for {image_path.name}: {e}")
                logger.debug(f"Raw response: {response.text[:500]}...")
                
                # Clean up uploaded file
                if img_file:
                    try:
                        genai.delete_file(img_file.name)
                    except:
                        pass
                
                # If using enhanced prompt and this is the last retry, try with simpler prompt
                if attempt == retries - 1 and self.use_enhanced_prompt:
                    logger.info("Retrying with simpler DEFAULT_PROMPT...")
                    try:
                        # Use simpler prompt with JSON mode
                        simple_prompt = self.DEFAULT_PROMPT.replace("video clip", "image frame").replace("this video", "this image")
                        
                        response = self.model.generate_content(
                            [simple_prompt, img_file],
                            generation_config={
                                "temperature": 0.3,
                                "max_output_tokens": 2048,
                                "response_mime_type": "application/json"  # Native JSON mode
                            }
                        )
                        
                        json_text = response.text.strip()
                        if json_text.startswith("```json"): json_text = json_text[7:]
                        if json_text.startswith("```"): json_text = json_text[3:]
                        if json_text.endswith("```"): json_text = json_text[:-3]
                        json_text = json_text.strip()
                        
                        # Robust JSON parsing with repair
                        try:
                            analysis = json.loads(json_text)
                        except json.JSONDecodeError as parse_err:
                            import re
                            json_text_fixed = re.sub(r',(\s*[}\]])', r'\1', json_text)
                            try:
                                analysis = json.loads(json_text_fixed)
                            except:
                                # Try truncation
                                depth = 0
                                last_valid = 0
                                for i, c in enumerate(json_text_fixed):
                                    if c in '{[': depth += 1
                                    elif c in '}]':
                                        depth -= 1
                                        if depth == 0: last_valid = i + 1
                                if last_valid > 0:
                                    analysis = json.loads(json_text_fixed[:last_valid])
                                else:
                                    raise parse_err
                        
                        # Clean malformed keys
                        def clean_dict_keys(obj):
                            if isinstance(obj, dict):
                                cleaned = {}
                                for key, value in obj.items():
                                    clean_key = key.replace('\n', '').replace('\t', '').replace('"', '').strip()
                                    cleaned[clean_key] = clean_dict_keys(value)
                                return cleaned
                            elif isinstance(obj, list):
                                return [clean_dict_keys(item) for item in obj]
                            else:
                                return obj
                        
                        analysis = clean_dict_keys(analysis)
                        
                        return {
                            "status": "success",
                            "clip_path": str(image_path),
                            "analysis": analysis,
                            "yolo_enhanced": bool(yolo_context),
                            "used_fallback_prompt": True
                        }
                    except Exception as fallback_error:
                        logger.error(f"Fallback prompt also failed: {fallback_error}")
                
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                    continue
                    
                return {
                    "status": "error",
                    "clip_path": str(image_path),
                    "error": f"JSON parse error: {str(e)}",
                    "raw_response": response.text[:1000] if 'response' in dir() else None
                }
            
            except Exception as e:
                logger.error(f"Image analysis error on attempt {attempt + 1}/{retries} for {image_path.name}: {type(e).__name__}: {e}")
                
                # Clean up uploaded file
                if img_file:
                    try:
                        genai.delete_file(img_file.name)
                    except:
                        pass
                
                if attempt < retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    logger.info(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                
                logger.error(f"All retries exhausted for {image_path.name}")
                return {
                    "status": "error",
                    "clip_path": str(image_path),
                    "error": f"{type(e).__name__}: {str(e)}"
                }
    
    def analyze_clip(self, clip_path: str, retries: int = 3, yolo_context: Optional[Dict] = None) -> Dict:
        """
        Analyze a single video clip or image using Gemini.
        
        Args:
            clip_path: Path to the video clip or image
            retries: Number of retry attempts on failure
            yolo_context: Optional YOLO detection context to enhance analysis
            
        Returns:
            Analysis result dict with 'status', 'clip_path', and 'analysis' or 'error'
        """
        clip_path = Path(clip_path)
        
        if clip_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
            return self.analyze_image(str(clip_path), retries, yolo_context)

        if not clip_path.exists():
            return {
                "status": "error",
                "clip_path": str(clip_path),
                "error": f"File not found: {clip_path}"
            }
        
        # Select prompt based on YOLO context availability
        if yolo_context and yolo_context.get('objects_detected'):
            prompt = self.DEFAULT_PROMPT_WITH_YOLO.format(
                yolo_context=f"Detected objects: {', '.join(yolo_context['objects_detected'])} ({yolo_context['num_objects']} total objects)"
            )
        else:
            prompt = self.prompt
        
        for attempt in range(retries):
            video_file = None
            try:
                # Upload video file to Gemini
                logger.debug(f"Uploading clip: {clip_path.name}")
                video_file = genai.upload_file(str(clip_path))
                
                # Wait for processing
                max_wait = 60  # Maximum wait time in seconds
                waited = 0
                while video_file.state.name == "PROCESSING" and waited < max_wait:
                    time.sleep(2)
                    waited += 2
                    video_file = genai.get_file(video_file.name)
                
                if video_file.state.name == "FAILED":
                    raise Exception(f"Video processing failed: {video_file.state.name}")
                
                if video_file.state.name == "PROCESSING":
                    raise Exception("Video processing timed out")
                
                # Generate analysis with JSON mode
                logger.debug(f"Analyzing clip: {clip_path.name}" + (" (with YOLO context)" if yolo_context else ""))
                response = self.model.generate_content(
                    [prompt, video_file],
                    generation_config={
                        "temperature": 0.3,
                        "max_output_tokens": 2048,
                        "response_mime_type": "application/json"  # Native JSON mode
                    }
                )
                
                # Parse JSON response with robust error handling
                json_text = response.text.strip()
                
                # Clean up common formatting issues
                if json_text.startswith("```json"):
                    json_text = json_text[7:]
                if json_text.startswith("```"):
                    json_text = json_text[3:]
                if json_text.endswith("```"):
                    json_text = json_text[:-3]
                json_text = json_text.strip()
                
                # Try parsing with robust error handling
                try:
                    analysis = json.loads(json_text)
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON parse error, attempting repair: {e}")
                    
                    import re
                    json_text_fixed = json_text
                    
                    # Fix 1: Remove trailing commas
                    json_text_fixed = re.sub(r',(\s*[}\]])', r'\1', json_text_fixed)
                    
                    try:
                        analysis = json.loads(json_text_fixed)
                        logger.debug(f"Successfully parsed JSON after repair")
                    except json.JSONDecodeError:
                        # Try extracting valid JSON portion
                        try:
                            depth = 0
                            last_valid_pos = 0
                            in_string = False
                            escape_next = False
                            
                            for i, char in enumerate(json_text_fixed):
                                if escape_next:
                                    escape_next = False
                                    continue
                                if char == '\\':
                                    escape_next = True
                                    continue
                                if char == '"' and not escape_next:
                                    in_string = not in_string
                                if not in_string:
                                    if char == '{' or char == '[':
                                        depth += 1
                                    elif char == '}' or char == ']':
                                        depth -= 1
                                        if depth == 0:
                                            last_valid_pos = i + 1
                            
                            if last_valid_pos > 0:
                                json_text_fixed = json_text_fixed[:last_valid_pos]
                                analysis = json.loads(json_text_fixed)
                                logger.debug(f"Successfully parsed truncated JSON")
                            else:
                                # Manual closure attempt
                                open_braces = json_text_fixed.count('{') - json_text_fixed.count('}')
                                open_brackets = json_text_fixed.count('[') - json_text_fixed.count(']')
                                if json_text_fixed.count('"') % 2 != 0:
                                    last_quote = json_text_fixed.rfind('"')
                                    if last_quote > 0:
                                        search_pos = last_quote - 1
                                        while search_pos > 0 and json_text_fixed[search_pos] not in [',', '{', '[']:
                                            search_pos -= 1
                                        if json_text_fixed[search_pos] == ',':
                                            json_text_fixed = json_text_fixed[:search_pos]
                                json_text_fixed += ']' * open_brackets + '}' * open_braces
                                analysis = json.loads(json_text_fixed)
                                logger.debug(f"Successfully parsed JSON after manual closure")
                        except:
                            raise e
                
                # Clean malformed keys with embedded newlines
                def clean_dict_keys(obj):
                    if isinstance(obj, dict):
                        cleaned = {}
                        for key, value in obj.items():
                            clean_key = key.replace('\n', '').replace('\t', '').replace('"', '').strip()
                            cleaned[clean_key] = clean_dict_keys(value)
                        return cleaned
                    elif isinstance(obj, list):
                        return [clean_dict_keys(item) for item in obj]
                    else:
                        return obj
                
                analysis = clean_dict_keys(analysis)
                
                # Clean up uploaded file
                try:
                    genai.delete_file(video_file.name)
                except:
                    pass  # Ignore cleanup errors
                
                logger.debug(f"Successfully analyzed: {clip_path.name}")
                
                return {
                    "status": "success",
                    "clip_path": str(clip_path),
                    "analysis": analysis,
                    "yolo_enhanced": bool(yolo_context)
                }
                
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parse error on attempt {attempt + 1}: {e}")
                if attempt < retries - 1:
                    time.sleep(2)
                    continue
                return {
                    "status": "error",
                    "clip_path": str(clip_path),
                    "error": f"JSON parse error: {str(e)}",
                    "raw_response": response.text if 'response' in dir() else None
                }
                
            except Exception as e:
                logger.warning(f"Analysis error on attempt {attempt + 1}: {e}")
                if attempt < retries - 1:
                    time.sleep(2)
                    continue
                return {
                    "status": "error",
                    "clip_path": str(clip_path),
                    "error": str(e)
                }
            
            finally:
                # Ensure cleanup
                if video_file:
                    try:
                        genai.delete_file(video_file.name)
                    except:
                        pass
    
    def analyze_clips_batch(
        self,
        clips: List[Dict],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[Dict]:
        """
        Analyze multiple clips with parallel processing.
        Automatically uses YOLO context if available in clip metadata.
        No artificial rate limiting - let the API handle it.
        
        Args:
            clips: List of clip info dicts (must have 'clip_path' key, optional 'yolo_context')
            progress_callback: Optional callback(current, total) for progress updates
            
        Returns:
            List of analysis results with clip_info merged
        """
        results = []
        total = len(clips)
        completed = 0
        
        logger.info(f"Starting batch analysis of {total} clips")
        
        # Check if any clips have YOLO context
        yolo_enhanced_count = sum(1 for c in clips if c.get('yolo_context'))
        if yolo_enhanced_count > 0:
            logger.info(f"  {yolo_enhanced_count} clips have YOLO context for enhanced analysis")
        
        # Process all clips in parallel - no artificial limits
        with ThreadPoolExecutor(max_workers=total) as executor:
            # Submit all tasks at once
            futures = {}
            for clip in clips:
                yolo_context = clip.get('yolo_context')
                future = executor.submit(self.analyze_clip, clip['clip_path'], yolo_context=yolo_context)
                futures[future] = clip
            
            # Collect results
            for future in as_completed(futures):
                clip_info = futures[future]
                try:
                    result = future.result()
                    # Merge clip info with analysis
                    result['clip_info'] = clip_info
                    results.append(result)
                    
                    # Log success/failure
                    if result['status'] == 'success':
                        logger.debug(f"✓ Clip {completed + 1}/{total} analyzed successfully")
                    else:
                        logger.warning(f"✗ Clip {completed + 1}/{total} failed: {result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    logger.error(f"✗ Clip {completed + 1}/{total} exception: {type(e).__name__}: {e}")
                    results.append({
                        "status": "error",
                        "clip_info": clip_info,
                        "clip_path": clip_info.get('clip_path'),
                        "error": f"{type(e).__name__}: {str(e)}"
                    })
                
                completed += 1
                if progress_callback:
                    progress_callback(completed, total)
        
        # Sort by original order
        results.sort(key=lambda x: x.get('clip_info', {}).get('clip_index', 0))
        
        success_count = sum(1 for r in results if r['status'] == 'success')
        yolo_enhanced = sum(1 for r in results if r.get('yolo_enhanced'))
        failed_count = total - success_count
        
        logger.info(f"Batch analysis complete: {success_count}/{total} successful")
        if yolo_enhanced > 0:
            logger.info(f"  {yolo_enhanced} analyses enhanced with YOLO context")
        
        # Log failed clips with error details
        if failed_count > 0:
            logger.error(f"  {failed_count} clips FAILED:")
            for r in results:
                if r['status'] != 'success':
                    clip_path = r.get('clip_path', 'unknown')
                    error = r.get('error', 'Unknown error')
                    logger.error(f"    ✗ {Path(clip_path).name}: {error}")
        
        return results
    
    def analyze_video_direct(
        self,
        video_path: str,
        max_duration: float = 120.0
    ) -> Dict:
        """
        Analyze an entire video directly (best for shorter videos < 2 min).
        Returns timestamped scene breakdowns.
        
        Args:
            video_path: Path to video file
            max_duration: Maximum video duration to process directly
            
        Returns:
            Dict with status and scenes array
        """
        video_file = None
        
        prompt = """Analyze this video for a film search engine.

For each distinct scene or shot in the video, provide:
- Approximate timestamp range (start and end in seconds)
- Scene type
- Brief description
- Mood
- Key visual elements
- Searchable tags

Format as a JSON array:
[
    {
        "start_time": 0.0,
        "end_time": 5.2,
        "scene_type": "establishing",
        "description": "Wide shot of city skyline at sunset",
        "mood": "peaceful",
        "key_elements": ["skyline", "sunset", "buildings"],
        "tags": ["city", "sunset", "establishing shot", "urban", "golden hour"]
    },
    ...
]

Respond with ONLY valid JSON array. No markdown, no explanation."""

        try:
            video_file = genai.upload_file(str(video_path))
            
            # Wait for processing
            max_wait = 120
            waited = 0
            while video_file.state.name == "PROCESSING" and waited < max_wait:
                time.sleep(2)
                waited += 2
                video_file = genai.get_file(video_file.name)
            
            if video_file.state.name != "ACTIVE":
                raise Exception(f"Video processing failed: {video_file.state.name}")
            
            response = self.model.generate_content(
                [prompt, video_file],
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 4096,
                    "response_mime_type": "application/json"  # Native JSON mode
                }
            )
            
            json_text = response.text.strip()
            if json_text.startswith("```"):
                json_text = json_text.split("```")[1]
                if json_text.startswith("json"):
                    json_text = json_text[4:]
            json_text = json_text.strip()
            
            scenes = json.loads(json_text)
            
            return {
                "status": "success",
                "video_path": str(video_path),
                "scenes": scenes
            }
            
        except Exception as e:
            logger.error(f"Direct video analysis failed: {e}")
            return {
                "status": "error",
                "video_path": str(video_path),
                "error": str(e)
            }
        
        finally:
            if video_file:
                try:
                    genai.delete_file(video_file.name)
                except:
                    pass


# Global instance for convenience
_analyzer: Optional[GeminiAnalyzer] = None


def get_analyzer(model_name: str = "gemini-2.5-flash") -> GeminiAnalyzer:
    """Get or create global analyzer instance."""
    global _analyzer
    if _analyzer is None:
        _analyzer = GeminiAnalyzer(model_name=model_name)
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
        clip_path = sys.argv[1]
        print(f"Analyzing: {clip_path}")
        
        try:
            result = analyze_clip(clip_path)
            
            if result['status'] == 'success':
                print("\n✅ Analysis successful!")
                print(json.dumps(result['analysis'], indent=2))
            else:
                print(f"\n❌ Error: {result['error']}")
                
        except ValueError as e:
            print(f"\nConfiguration error: {e}")
            print("Make sure GEMINI_API_KEY is set in your environment or .env file")
    else:
        print("Usage: python gemini_analyzer.py <clip_path>")
        print("\nMake sure to set GEMINI_API_KEY environment variable first.")
