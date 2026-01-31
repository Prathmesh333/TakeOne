"""
Test script to diagnose Gemini analysis issues with a single thumbnail
"""

import sys
import logging
from pathlib import Path
from ingestion.gemini_analyzer import GeminiAnalyzer

# Enable DEBUG logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s:%(name)s:%(message)s'
)

def test_single_thumbnail(thumbnail_path: str):
    """Test analyzing a single thumbnail"""
    print(f"\n{'='*60}")
    print(f"Testing Gemini Analysis")
    print(f"{'='*60}")
    print(f"Thumbnail: {thumbnail_path}")
    
    # Check if file exists
    thumb_path = Path(thumbnail_path)
    if not thumb_path.exists():
        print(f"❌ ERROR: File not found: {thumbnail_path}")
        return
    
    print(f"✓ File exists: {thumb_path.stat().st_size} bytes")
    
    # Initialize analyzer with simpler prompt
    print("\nInitializing Gemini analyzer (simple prompt)...")
    analyzer = GeminiAnalyzer(
        model_name="gemini-2.5-flash",
        use_enhanced_prompt=False  # Use simpler prompt
    )
    
    # Test analysis
    print("\nAnalyzing thumbnail...")
    result = analyzer.analyze_image(thumbnail_path, retries=3)
    
    print(f"\n{'='*60}")
    print("RESULT")
    print(f"{'='*60}")
    
    if result['status'] == 'success':
        print("✅ SUCCESS!")
        print(f"\nAnalysis:")
        import json
        print(json.dumps(result['analysis'], indent=2))
    else:
        print("❌ FAILED!")
        print(f"\nError: {result.get('error', 'Unknown error')}")
        if result.get('raw_response'):
            print(f"\nRaw response (first 500 chars):")
            print(result['raw_response'][:500])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_gemini_single.py <thumbnail_path>")
        print("\nExample:")
        print("  python test_gemini_single.py output/thumbnails/video_name/scene_0001.jpg")
        sys.exit(1)
    
    test_single_thumbnail(sys.argv[1])
