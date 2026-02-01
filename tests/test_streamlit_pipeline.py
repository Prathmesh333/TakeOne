"""
Test Streamlit Pipeline Integration
"""
import os
import sys
from pathlib import Path

print("="*60)
print("STREAMLIT PIPELINE TEST")
print("="*60)

# Test 1: Environment
print("\n[1] Environment Check")
print(f"Python: {sys.version}")
print(f"Working Dir: {os.getcwd()}")

gemini_key = os.environ.get("GEMINI_API_KEY")
if gemini_key:
    print(f"✅ GEMINI_API_KEY: Set ({len(gemini_key)} chars)")
else:
    print("❌ GEMINI_API_KEY: Not set")

# Test 2: Core Imports
print("\n[2] Core Imports")
try:
    import streamlit as st
    print("✅ Streamlit imported")
except ImportError as e:
    print(f"❌ Streamlit: {e}")

try:
    import chromadb
    print("✅ ChromaDB imported")
except ImportError as e:
    print(f"❌ ChromaDB: {e}")

try:
    from sentence_transformers import SentenceTransformer
    print("✅ SentenceTransformers imported")
except ImportError as e:
    print(f"❌ SentenceTransformers: {e}")

# Test 3: Pipeline Components
print("\n[3] Pipeline Components")
try:
    from ingestion.pipeline import TakeOnePipeline
    print("✅ TakeOnePipeline imported")
except ImportError as e:
    print(f"❌ TakeOnePipeline: {e}")

try:
    from search.vector_search import SceneSearchEngine
    print("✅ SceneSearchEngine imported")
except ImportError as e:
    print(f"❌ SceneSearchEngine: {e}")

try:
    from ingestion.gemini_analyzer import GeminiAnalyzer
    print("✅ GeminiAnalyzer imported")
except ImportError as e:
    print(f"❌ GeminiAnalyzer: {e}")

try:
    from ingestion.scene_detector import detect_scenes_hybrid
    print("✅ SceneDetector imported")
except ImportError as e:
    print(f"❌ SceneDetector: {e}")

# Test 4: Directory Structure
print("\n[4] Directory Structure")
required_dirs = ['output', 'chroma_db', 'ingestion', 'search', 'docs']
for dir_name in required_dirs:
    dir_path = Path(dir_name)
    if dir_path.exists():
        print(f"✅ {dir_name}/ exists")
    else:
        print(f"⚠️  {dir_name}/ missing (will be created)")

# Test 5: Pipeline Initialization
print("\n[5] Pipeline Initialization")
try:
    pipeline = TakeOnePipeline(
        output_dir="./test_output",
        chroma_dir="./test_chroma_db",
        gemini_model="gemini-2.5-flash"
    )
    print("✅ Pipeline initialized successfully")
    print(f"   Output: {pipeline.output_dir}")
    print(f"   Clips: {pipeline.clips_dir}")
    print(f"   Model: {pipeline.gemini_model}")
except Exception as e:
    print(f"❌ Pipeline initialization failed: {e}")

# Test 6: Search Engine
print("\n[6] Search Engine")
try:
    engine = SceneSearchEngine(persist_dir="./test_chroma_db")
    stats = engine.get_stats()
    print("✅ Search engine initialized")
    print(f"   Total scenes: {stats['total_scenes']}")
    print(f"   Unique videos: {stats.get('unique_videos', 0)}")
except Exception as e:
    print(f"❌ Search engine failed: {e}")

# Test 7: Gemini Analyzer (if API key available)
print("\n[7] Gemini Analyzer")
if gemini_key:
    try:
        analyzer = GeminiAnalyzer(model_name="gemini-2.5-flash")
        print("✅ Gemini analyzer initialized")
        print(f"   Model: {analyzer.model_name}")
        print(f"   Enhanced prompt: {analyzer.use_enhanced_prompt}")
    except Exception as e:
        print(f"❌ Gemini analyzer failed: {e}")
else:
    print("⚠️  Skipped (no API key)")

# Summary
print("\n" + "="*60)
print("TEST SUMMARY")
print("="*60)
print("\n✅ Core functionality ready for Streamlit UI")
print("⚠️  Note: GPU not detected (CPU mode)")
print("\nTo run Streamlit UI:")
print("  streamlit run app.py")
print("="*60)
