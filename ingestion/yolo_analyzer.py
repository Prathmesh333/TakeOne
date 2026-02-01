"""
YOLO Analyzer - Fast semantic scene description using YOLO detections
Provides quick scene understanding before expensive Gemini analysis
"""

import cv2
import numpy as np
import logging
from pathlib import Path
from typing import Dict, List, Optional
from collections import Counter

logger = logging.getLogger(__name__)


class YOLOAnalyzer:
    """
    Generates semantic scene descriptions using YOLO object detections.
    Much faster than Gemini, used for initial filtering and context.
    """
    
    def __init__(self, model_name: str = "yolov8n.pt", use_gpu: bool = True):
        """
        Initialize YOLO analyzer.
        
        Args:
            model_name: YOLO model (yolov8n.pt is fastest)
            use_gpu: Whether to use GPU acceleration (default: True)
        """
        self.model_name = model_name
        self.use_gpu = use_gpu
        self._model = None
        
    @property
    def model(self):
        """Lazy load YOLO model."""
        if self._model is None:
            try:
                from ultralytics import YOLO
                import torch
                
                logger.info(f"Loading YOLO model: {self.model_name}")
                self._model = YOLO(self.model_name)
                
                # Auto-detect and use GPU if available
                if self.use_gpu and torch.cuda.is_available():
                    self._model.to('cuda')
                    logger.info(" YOLO running on GPU (CUDA)")
                elif self.use_gpu:
                    logger.warning(" GPU requested but CUDA not available, using CPU")
                else:
                    logger.info("YOLO running on CPU")
                    
            except ImportError:
                logger.error("Ultralytics not installed. Install with: pip install ultralytics")
                raise ImportError("Ultralytics required for YOLOAnalyzer")
                
        return self._model
    
    def analyze_frame(self, frame) -> Dict:
        """
        Analyze a single frame and generate semantic description.
        
        Args:
            frame: OpenCV image (numpy array)
            
        Returns:
            Dict with semantic analysis
        """
        try:
            results = self.model(frame, verbose=False)
            
            if not results or not results[0].boxes:
                return {
                    'objects': [],
                    'object_counts': {},
                    'scene_complexity': 0,
                    'description': "Empty or unclear scene",
                    'confidence': 0.0
                }
            
            boxes = results[0].boxes
            
            # Extract detections
            detections = []
            object_names = []
            confidences = []
            
            for i in range(len(boxes)):
                box = boxes[i]
                class_id = int(box.cls[0])
                class_name = self.model.names[class_id]
                confidence = float(box.conf[0])
                
                detections.append({
                    'class_name': class_name,
                    'confidence': confidence,
                    'bbox': box.xyxy[0].tolist()
                })
                
                object_names.append(class_name)
                confidences.append(confidence)
            
            # Count objects
            object_counts = dict(Counter(object_names))
            
            # Calculate scene complexity
            complexity = len(set(object_names)) + (len(detections) / 10)
            
            # Generate description
            description = self._generate_description(object_counts, detections, frame.shape)
            
            # Average confidence
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return {
                'objects': detections,
                'object_counts': object_counts,
                'scene_complexity': complexity,
                'description': description,
                'confidence': avg_confidence,
                'total_objects': len(detections)
            }
            
        except Exception as e:
            logger.error(f"Frame analysis error: {e}")
            return {
                'objects': [],
                'object_counts': {},
                'scene_complexity': 0,
                'description': "Analysis failed",
                'confidence': 0.0,
                'error': str(e)
            }
    
    def analyze_clip(self, clip_path: str, num_samples: int = 5) -> Dict:
        """
        Analyze a video clip by sampling multiple frames.
        
        Args:
            clip_path: Path to video clip
            num_samples: Number of frames to sample
            
        Returns:
            Dict with aggregated semantic analysis
        """
        clip_path = Path(clip_path)
        
        if not clip_path.exists():
            return {
                'status': 'error',
                'error': f"File not found: {clip_path}"
            }
        
        cap = cv2.VideoCapture(str(clip_path))
        if not cap.isOpened():
            return {
                'status': 'error',
                'error': f"Could not open video: {clip_path}"
            }
        
        try:
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration = total_frames / fps if fps > 0 else 0
            
            # Sample frames evenly
            sample_indices = np.linspace(0, total_frames - 1, num_samples, dtype=int)
            
            frame_analyses = []
            all_objects = []
            all_confidences = []
            
            for frame_idx in sample_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if not ret:
                    continue
                
                analysis = self.analyze_frame(frame)
                frame_analyses.append(analysis)
                
                all_objects.extend([obj['class_name'] for obj in analysis.get('objects', [])])
                all_confidences.extend([obj['confidence'] for obj in analysis.get('objects', [])])
            
            cap.release()
            
            if not frame_analyses:
                return {
                    'status': 'error',
                    'error': 'No frames could be analyzed'
                }
            
            # Aggregate results
            object_counts = dict(Counter(all_objects))
            avg_complexity = sum(a['scene_complexity'] for a in frame_analyses) / len(frame_analyses)
            avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0.0
            
            # Generate clip description
            description = self._generate_clip_description(object_counts, avg_complexity, duration)
            
            # Determine if this clip needs Gemini analysis
            needs_gemini = self._should_use_gemini(object_counts, avg_complexity, avg_confidence)
            
            return {
                'status': 'success',
                'clip_path': str(clip_path),
                'duration': duration,
                'object_counts': object_counts,
                'total_objects': len(all_objects),
                'unique_objects': len(object_counts),
                'scene_complexity': avg_complexity,
                'confidence': avg_confidence,
                'description': description,
                'needs_gemini': needs_gemini,
                'frame_analyses': frame_analyses
            }
            
        except Exception as e:
            logger.error(f"Clip analysis error: {e}")
            return {
                'status': 'error',
                'clip_path': str(clip_path),
                'error': str(e)
            }
        finally:
            cap.release()
    
    def _generate_description(self, object_counts: Dict, detections: List, frame_shape) -> str:
        """Generate natural language description from detections."""
        if not object_counts:
            return "Empty or unclear scene"
        
        # Sort by count
        sorted_objects = sorted(object_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Build description
        parts = []
        
        # Main objects
        if sorted_objects:
            main_obj, count = sorted_objects[0]
            if count > 1:
                parts.append(f"{count} {main_obj}s")
            else:
                parts.append(f"a {main_obj}")
        
        # Additional objects
        if len(sorted_objects) > 1:
            other_objects = [obj for obj, _ in sorted_objects[1:4]]  # Top 3 additional
            if other_objects:
                parts.append(f"with {', '.join(other_objects)}")
        
        # Scene type inference
        scene_type = self._infer_scene_type(object_counts)
        if scene_type:
            parts.append(f"({scene_type})")
        
        return " ".join(parts)
    
    def _generate_clip_description(self, object_counts: Dict, complexity: float, duration: float) -> str:
        """Generate description for entire clip."""
        if not object_counts:
            return "Empty or unclear clip"
        
        sorted_objects = sorted(object_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Main subjects
        main_objects = []
        for obj, count in sorted_objects[:3]:
            if count > 1:
                main_objects.append(f"{count} {obj}s")
            else:
                main_objects.append(f"{obj}")
        
        # Scene type
        scene_type = self._infer_scene_type(object_counts)
        
        # Complexity indicator
        if complexity > 5:
            complexity_desc = "complex"
        elif complexity > 3:
            complexity_desc = "moderate"
        else:
            complexity_desc = "simple"
        
        description = f"{complexity_desc.capitalize()} {scene_type or 'scene'} with {', '.join(main_objects)}"
        
        return description
    
    def _infer_scene_type(self, object_counts: Dict) -> Optional[str]:
        """Infer scene type from detected objects."""
        objects = set(object_counts.keys())
        
        # Indoor indicators
        indoor_objects = {'couch', 'chair', 'tv', 'laptop', 'keyboard', 'mouse', 'bed', 'dining table'}
        # Outdoor indicators
        outdoor_objects = {'car', 'truck', 'tree', 'traffic light', 'stop sign', 'bench', 'bird'}
        # People-focused
        people_objects = {'person'}
        
        indoor_score = len(objects & indoor_objects)
        outdoor_score = len(objects & outdoor_objects)
        
        if 'person' in objects:
            if indoor_score > outdoor_score:
                return "indoor scene"
            elif outdoor_score > indoor_score:
                return "outdoor scene"
            else:
                return "scene with people"
        elif indoor_score > 0:
            return "indoor setting"
        elif outdoor_score > 0:
            return "outdoor setting"
        
        return None
    
    def _should_use_gemini(self, object_counts: Dict, complexity: float, confidence: float) -> bool:
        """
        Determine if this clip needs detailed Gemini analysis.
        
        Criteria:
        - High complexity (many objects/actions)
        - People present (emotions matter)
        - High confidence (clear scene)
        - Interesting objects (not just background)
        """
        # Always analyze if people are present (emotions!)
        if 'person' in object_counts:
            return True
        
        # High complexity scenes
        if complexity > 4:
            return True
        
        # High confidence with interesting objects
        if confidence > 0.7 and len(object_counts) > 2:
            return True
        
        # Otherwise, YOLO description is sufficient
        return False


def analyze_clips_batch(
    clips: List[Dict],
    use_gpu: bool = False,
    num_samples: int = 5
) -> List[Dict]:
    """
    Analyze multiple clips with YOLO.
    
    Args:
        clips: List of clip info dicts with 'clip_path'
        use_gpu: Whether to use GPU
        num_samples: Frames to sample per clip
        
    Returns:
        List of YOLO analysis results
    """
    analyzer = YOLOAnalyzer(use_gpu=use_gpu)
    
    results = []
    for clip in clips:
        logger.info(f"YOLO analyzing: {Path(clip['clip_path']).name}")
        analysis = analyzer.analyze_clip(clip['clip_path'], num_samples)
        
        # Merge with clip info
        analysis['clip_info'] = clip
        results.append(analysis)
    
    return results


if __name__ == "__main__":
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    if len(sys.argv) > 1:
        clip_path = sys.argv[1]
        print(f"Analyzing: {clip_path}")
        
        analyzer = YOLOAnalyzer()
        result = analyzer.analyze_clip(clip_path)
        
        if result['status'] == 'success':
            print(f"\nAnalysis successful!")
            print(f"Description: {result['description']}")
            print(f"Objects: {result['object_counts']}")
            print(f"Complexity: {result['scene_complexity']:.2f}")
            print(f"Confidence: {result['confidence']:.2f}")
            print(f"Needs Gemini: {result['needs_gemini']}")
        else:
            print(f"\nError: {result['error']}")
    else:
        print("Usage: python yolo_analyzer.py <clip_path>")
