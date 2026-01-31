"""
Frame Selector - Intelligent frame selection using YOLO
Selects the most representative frame from a scene based on object detection scores.
"""

import cv2
import numpy as np
import logging
from pathlib import Path
from typing import List, Tuple, Optional, Dict

logger = logging.getLogger(__name__)

class FrameSelector:
    """
    Selects the best frame from a video segment using YOLO object detection.
    """
    
    def __init__(self, model_name: str = "yolov8n.pt", use_gpu: bool = False):
        """
        Initialize the frame selector.
        
        Args:
            model_name: YOLO model name (yolov8n.pt is smallest/fastest)
            use_gpu: Whether to use GPU acceleration
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
                
                if self.use_gpu and torch.cuda.is_available():
                    self._model.to('cuda')
                    logger.info("YOLO running on GPU")
                else:
                    logger.info("YOLO running on CPU")
                    
            except ImportError:
                logger.error("Ultralytics not installed. Install with: pip install ultralytics")
                raise ImportError("Ultralytics required for FrameSelector")
                
        return self._model

    def select_best_frame(
        self,
        video_path: str,
        start_time: float,
        end_time: float,
        samples: int = 5
    ) -> Optional[Dict]:
        """
        Select the best frame from a scene with YOLO detection context.
        
        Args:
            video_path: Path to video file
            start_time: Start time in seconds
            end_time: End time in seconds
            samples: Number of frames to sample and score
            
        Returns:
            Dict with 'time', 'score', 'image' (numpy array), 'detections', or None
        """
        if end_time <= start_time:
            return None
            
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            logger.error(f"Could not open video: {video_path}")
            return None
            
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = end_time - start_time
        
        # Determine sample timestamps
        # Avoid exactly start/end to avoid black fade-ins/outs
        safe_margin = min(0.5, duration * 0.1)
        sample_times = np.linspace(
            start_time + safe_margin,
            end_time - safe_margin,
            samples
        )
        
        best_frame = None
        best_score = -1
        
        try:
            for t in sample_times:
                # Seek to frame
                frame_idx = int(t * fps)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                
                ret, frame = cap.read()
                if not ret:
                    continue
                
                # Score frame using YOLO and get detections
                score, detections = self._score_frame_with_context(frame)
                
                logger.debug(f"Time {t:.2f}s: Score {score:.2f}, Objects: {len(detections)}")
                
                if score > best_score:
                    best_score = score
                    best_frame = {
                        'time': t,
                        'score': score,
                        'image': frame,
                        'detections': detections  # Include YOLO detections
                    }
                    
        except Exception as e:
            logger.error(f"Error selecting frame: {e}")
        finally:
            cap.release()
            
        return best_frame

    def _score_frame_with_context(self, frame) -> Tuple[float, List[Dict]]:
        """
        Score a frame and return detection context.
        Returns: (score, detections_list)
        """
        try:
            results = self.model(frame, verbose=False)
            
            if not results or not results[0].boxes:
                return 0.0, []
                
            boxes = results[0].boxes
            
            # Extract detection information
            detections = []
            for i in range(len(boxes)):
                box = boxes[i]
                detections.append({
                    'class_id': int(box.cls[0]),
                    'class_name': self.model.names[int(box.cls[0])],
                    'confidence': float(box.conf[0]),
                    'bbox': box.xyxy[0].tolist()
                })
            
            # Simple scoring: sum of confidences + bonus for unique classes
            conf_sum = float(boxes.conf.sum())
            unique_classes = len(set(boxes.cls.tolist()))
            
            # Prefer larger objects (better visible)
            h, w = frame.shape[:2]
            total_area = h * w
            object_area = sum([(box[2]-box[0])*(box[3]-box[1]) for box in boxes.xyxy.tolist()])
            area_score = min(1.0, object_area / total_area) * 2
            
            # Weighted score
            final_score = (conf_sum * 0.5) + (unique_classes * 1.0) + area_score
            
            return float(final_score), detections
            
        except Exception as e:
            logger.error(f"Scoring error: {e}")
            return 0.0, []

def save_frame(frame_data: Dict, output_path: str):
    """Save the selected frame to disk."""
    if frame_data and frame_data.get('image') is not None:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(output_path, frame_data['image'])
        return True
    return False
