"""
TakeOne - Test Script
Tests the pipeline components without requiring video files
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()


def check_dependencies():
    """Check if all required dependencies are installed."""
    print("📦 Checking dependencies...\n")
    
    dependencies = {
        "streamlit": "Core web framework",
        "chromadb": "Vector database",
        "sentence_transformers": "Text embeddings",
        "google.generativeai": "Gemini API",
        "scenedetect": "Scene detection",
        "cv2": "Video processing (OpenCV)",
        "PIL": "Image processing",
        "torch": "PyTorch (for CLIP)",
        "transformers": "HuggingFace (for CLIP)",
        "numpy": "Numerical computing",
        "tqdm": "Progress bars"
    }
    
    results = {}
    
    for module, description in dependencies.items():
        try:
            if module == "cv2":
                import cv2
            elif module == "PIL":
                from PIL import Image
            elif module == "google.generativeai":
                import google.generativeai
            elif module == "sentence_transformers":
                from sentence_transformers import SentenceTransformer
            else:
                __import__(module)
            results[module] = True
            print(f"✅ {module}: {description}")
        except ImportError:
            results[module] = False
            print(f"❌ {module}: {description} - NOT INSTALLED")
    
    return all(results.values())


def check_ffmpeg():
    """Check if FFmpeg is installed."""
    print("\n🎬 Checking FFmpeg...")
    
    import subprocess
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"✅ FFmpeg installed: {version[:50]}...")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ FFmpeg not found. Please install FFmpeg and add to PATH.")
    print("   Windows: choco install ffmpeg")
    print("   Mac: brew install ffmpeg")
    print("   Linux: sudo apt install ffmpeg")
    return False


def check_api_key():
    """Check if Gemini API key is configured."""
    print("\n🔑 Checking API keys...")
    
    gemini_key = os.environ.get("GEMINI_API_KEY")
    
    if gemini_key and gemini_key != "your_gemini_api_key_here":
        print(f"✅ GEMINI_API_KEY is set ({gemini_key[:10]}...)")
        return True
    else:
        print("⚠️ GEMINI_API_KEY not set or using placeholder")
        print("   Set it in .env file or environment")
        print("   Get a key at: https://aistudio.google.com")
        return False


def test_scene_detector():
    """Test the scene detector module."""
    print("\n🎯 Testing Scene Detector...")
    
    try:
        from ingestion.scene_detector import detect_scenes, smart_split_scenes, get_scene_stats
        
        # Test with mock data
        mock_scenes = [(0, 5), (5, 20), (20, 21), (21, 30)]
        optimized = smart_split_scenes(mock_scenes, max_duration=10, min_duration=2)
        stats = get_scene_stats(optimized)
        
        print(f"✅ Scene detector loaded successfully")
        print(f"   Mock input: {len(mock_scenes)} scenes")
        print(f"   After optimization: {len(optimized)} scenes")
        print(f"   Avg duration: {stats['avg_duration']:.1f}s")
        return True
        
    except Exception as e:
        print(f"❌ Scene detector error: {e}")
        return False


def test_video_clipper():
    """Test the video clipper module (imports only)."""
    print("\n✂️ Testing Video Clipper...")
    
    try:
        from ingestion.video_clipper import extract_clip, extract_all_clips, get_video_info
        
        print("✅ Video clipper loaded successfully")
        return True
        
    except Exception as e:
        print(f"❌ Video clipper error: {e}")
        return False


def test_gemini_analyzer():
    """Test the Gemini analyzer module."""
    print("\n🤖 Testing Gemini Analyzer...")
    
    try:
        from ingestion.gemini_analyzer import GeminiAnalyzer
        
        if os.environ.get("GEMINI_API_KEY"):
            # Just test initialization
            analyzer = GeminiAnalyzer()
            print(f"✅ Gemini analyzer initialized: {analyzer.model_name}")
        else:
            print("⚠️ Skipped (no API key)")
        return True
        
    except Exception as e:
        print(f"❌ Gemini analyzer error: {e}")
        return False


def test_search_engine():
    """Test the search engine."""
    print("\n🔍 Testing Search Engine...")
    
    try:
        from search.vector_search import SceneSearchEngine
        
        # Initialize with test collection
        engine = SceneSearchEngine(
            persist_dir="./test_chroma_db",
            collection_name="test_scenes"
        )
        
        stats = engine.get_stats()
        print(f"✅ Search engine initialized")
        print(f"   Collection has {stats['total_scenes']} scenes")
        
        # Test indexing a mock scene
        mock_clip_info = {
            "video_id": "test_video",
            "clip_path": "/test/clip.mp4",
            "start_time": 0,
            "end_time": 5,
            "duration": 5,
            "clip_index": 0
        }
        mock_analysis = {
            "scene_type": "dialogue",
            "description": "Two people having a conversation in a coffee shop",
            "mood": "casual",
            "tags": ["conversation", "coffee", "indoor", "dialogue"]
        }
        
        success = engine.index_scene("test_scene_001", mock_clip_info, mock_analysis)
        
        if success:
            print("✅ Scene indexing works")
            
            # Test search
            results = engine.search("people talking", top_k=5)
            print(f"✅ Search works - found {len(results)} results")
        
        # Cleanup
        engine.clear()
        
        return True
        
    except Exception as e:
        print(f"❌ Search engine error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pipeline():
    """Test the pipeline orchestrator."""
    print("\n🔄 Testing Pipeline...")
    
    try:
        from ingestion.pipeline import TakeOnePipeline
        
        pipeline = TakeOnePipeline(
            output_dir="./test_output",
            chroma_dir="./test_chroma_db"
        )
        
        print(f"✅ Pipeline initialized")
        print(f"   Output dir: {pipeline.output_dir}")
        print(f"   Model: {pipeline.gemini_model}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pipeline error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("🎬 TakeOne - System Test")
    print("=" * 60)
    
    tests = [
        ("Dependencies", check_dependencies),
        ("FFmpeg", check_ffmpeg),
        ("API Key", check_api_key),
        ("Scene Detector", test_scene_detector),
        ("Video Clipper", test_video_clipper),
        ("Gemini Analyzer", test_gemini_analyzer),
        ("Search Engine", test_search_engine),
        ("Pipeline", test_pipeline),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"❌ {name} failed with exception: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for name, result in results.items():
        status = "✅" if result else "❌"
        print(f"  {status} {name}")
    
    print(f"\n{'✅' if passed == total else '⚠️'} {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! TakeOne is ready to use.")
        print("   Run: streamlit run app.py")
    else:
        print("\n⚠️ Some tests failed. Please fix the issues above.")
    
    # Cleanup test directories
    import shutil
    for test_dir in ["./test_output", "./test_chroma_db"]:
        if Path(test_dir).exists():
            shutil.rmtree(test_dir)


if __name__ == "__main__":
    main()
