"""
Test script to verify YOLO integration is working properly.
"""

import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def test_yolo_import():
    """Test if YOLO can be imported."""
    try:
        from ultralytics import YOLO
        logger.info("PASS: Ultralytics YOLO imported successfully")
        return True
    except ImportError as e:
        logger.error(f"FAIL: Failed to import YOLO: {e}")
        logger.error("  Install with: pip install ultralytics")
        return False


def test_yolo_model_load():
    """Test if YOLO model can be loaded."""
    try:
        from ultralytics import YOLO
        logger.info("Loading YOLOv8n model...")
        model = YOLO("yolov8n.pt")
        logger.info("PASS: YOLO model loaded successfully")
        
        # Check GPU availability
        import torch
        if torch.cuda.is_available():
            logger.info(f"INFO: GPU available: {torch.cuda.get_device_name(0)}")
        else:
            logger.info("INFO: GPU not available, will use CPU")
        
        return True
    except Exception as e:
        logger.error(f"FAIL: Failed to load YOLO model: {e}")
        return False


def test_frame_selector():
    """Test FrameSelector initialization."""
    try:
        from ingestion.frame_selector import FrameSelector
        logger.info("Initializing FrameSelector...")
        selector = FrameSelector()
        # Force model load
        _ = selector.model
        logger.info("PASS: FrameSelector initialized successfully")
        return True
    except Exception as e:
        logger.error(f"FAIL: Failed to initialize FrameSelector: {e}")
        return False


def test_scene_detector():
    """Test YOLO scene detection functions."""
    try:
        from ingestion.scene_detector import detect_scenes_yolo, _create_semantic_signature
        logger.info("PASS: YOLO scene detection functions imported successfully")
        return True
    except Exception as e:
        logger.error(f"FAIL: Failed to import scene detection functions: {e}")
        return False


def test_video_processing(video_path: str):
    """Test full YOLO pipeline on a video."""
    if not Path(video_path).exists():
        logger.warning(f"WARNING: Video not found: {video_path}")
        logger.warning("  Skipping video processing test")
        return None
    
    try:
        from ingestion.scene_detector import detect_scenes_yolo
        from ingestion.frame_selector import FrameSelector
        
        logger.info(f"\nTesting YOLO scene detection on: {video_path}")
        
        # Test scene detection
        scenes = detect_scenes_yolo(
            video_path,
            threshold=0.4,
            min_scene_len=2.0,
            sample_rate=5
        )
        
        logger.info(f"PASS: Detected {len(scenes)} scenes")
        
        if len(scenes) > 0:
            # Test frame selection on first scene
            logger.info("\nTesting YOLO frame selection on first scene...")
            selector = FrameSelector()
            
            start, end = scenes[0]
            frame_data = selector.select_best_frame(
                video_path,
                start_time=start,
                end_time=end,
                samples=3
            )
            
            if frame_data:
                logger.info(f"PASS: Selected frame at {frame_data['time']:.2f}s")
                logger.info(f"  Score: {frame_data['score']:.2f}")
                logger.info(f"  Detections: {len(frame_data.get('detections', []))} objects")
                
                if frame_data.get('detections'):
                    objects = [d['class_name'] for d in frame_data['detections'][:5]]
                    logger.info(f"  Objects: {', '.join(objects)}")
            else:
                logger.warning("WARNING: Frame selection returned None")
        
        return True
        
    except Exception as e:
        logger.error(f"FAIL: Video processing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pipeline_integration():
    """Test pipeline with YOLO flags."""
    try:
        from ingestion.pipeline import TakeOnePipeline
        logger.info("\nTesting pipeline initialization with YOLO...")
        
        pipeline = TakeOnePipeline(output_dir="./test_output")
        logger.info("PASS: Pipeline initialized successfully")
        
        # Check if process_video accepts YOLO parameters
        import inspect
        sig = inspect.signature(pipeline.process_video)
        params = list(sig.parameters.keys())
        
        if 'use_yolo' in params:
            logger.info("PASS: Pipeline supports use_yolo parameter")
        else:
            logger.warning("WARNING: Pipeline missing use_yolo parameter")
        
        if 'yolo_scene_detection' in params:
            logger.info("PASS: Pipeline supports yolo_scene_detection parameter")
        else:
            logger.warning("WARNING: Pipeline missing yolo_scene_detection parameter")
        
        return True
        
    except Exception as e:
        logger.error(f"FAIL: Pipeline integration test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("YOLO Integration Test Suite")
    print("="*60)
    
    results = {}
    
    # Basic tests
    print("\n1. Testing YOLO Import...")
    results['import'] = test_yolo_import()
    
    if results['import']:
        print("\n2. Testing YOLO Model Load...")
        results['model'] = test_yolo_model_load()
    else:
        results['model'] = False
        logger.warning("WARNING: Skipping model test (import failed)")
    
    print("\n3. Testing FrameSelector...")
    results['frame_selector'] = test_frame_selector()
    
    print("\n4. Testing Scene Detector...")
    results['scene_detector'] = test_scene_detector()
    
    print("\n5. Testing Pipeline Integration...")
    results['pipeline'] = test_pipeline_integration()
    
    # Video test (optional)
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
        print(f"\n6. Testing Video Processing...")
        results['video'] = test_video_processing(video_path)
    else:
        logger.info("\n6. Video Processing Test")
        logger.info("  Skipped (no video provided)")
        logger.info("  Usage: python test_yolo_integration.py <video_path>")
        results['video'] = None
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)
    
    for test_name, result in results.items():
        if result is True:
            status = "PASS"
        elif result is False:
            status = "FAIL"
        else:
            status = "SKIP"
        print(f"[{status}] {test_name}")
    
    print(f"\nTotal: {passed} passed, {failed} failed, {skipped} skipped")
    
    if failed == 0:
        print("\nAll tests passed! YOLO integration is working properly.")
        return 0
    else:
        print("\nSome tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
