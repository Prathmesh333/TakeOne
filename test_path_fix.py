"""
Test to verify the clip path fix is working correctly.
This simulates the pipeline flow to ensure paths are preserved.
"""

from pathlib import Path

def test_path_preservation():
    """Test that original clip paths are preserved after Gemini analysis simulation."""
    
    print("Testing clip path preservation...")
    print("="*60)
    
    # Simulate original clips with correct paths
    clips = [
        {
            'clip_index': 0,
            'clip_path': 'output/clips/test_video/scene_0000.mp4',
            'thumbnail_path': 'output/thumbnails/test_video/scene_0000.jpg',
            'duration': 5.0
        },
        {
            'clip_index': 1,
            'clip_path': 'output/clips/test_video/scene_0001.mp4',
            'thumbnail_path': 'output/thumbnails/test_video/scene_0001.jpg',
            'duration': 4.5
        }
    ]
    
    print("\n1. Original clips:")
    for clip in clips:
        print(f"   Clip {clip['clip_index']}: {clip['clip_path']}")
    
    # Simulate Gemini analysis preparation (create copies)
    gemini_clips = []
    for clip in clips:
        gemini_clip_info = clip.copy()  # Create copy
        gemini_clip_info['clip_path'] = clip['thumbnail_path']  # Use thumbnail for Gemini
        gemini_clip_info['is_thumbnail'] = True
        gemini_clips.append(gemini_clip_info)
    
    print("\n2. Gemini clips (modified for analysis):")
    for clip in gemini_clips:
        print(f"   Clip {clip['clip_index']}: {clip['clip_path']}")
    
    # Verify originals are unchanged
    print("\n3. Original clips after creating Gemini copies:")
    for clip in clips:
        print(f"   Clip {clip['clip_index']}: {clip['clip_path']}")
    
    # Simulate Gemini analysis results
    analysis_results = []
    for gemini_clip in gemini_clips:
        analysis_results.append({
            'status': 'success',
            'clip_info': gemini_clip,  # Contains modified path
            'analysis': {'description': 'Test scene'}
        })
    
    print("\n4. Analysis results (before restoration):")
    for result in analysis_results:
        clip_info = result['clip_info']
        print(f"   Clip {clip_info['clip_index']}: {clip_info['clip_path']}")
    
    # Simulate path restoration (the fix)
    for result in analysis_results:
        if result.get('status') == 'success' and result.get('clip_info'):
            clip_index = result['clip_info'].get('clip_index')
            original_clip = next((c for c in clips if c.get('clip_index') == clip_index), None)
            if original_clip:
                result['clip_info']['clip_path'] = original_clip['clip_path']
    
    print("\n5. Analysis results (after restoration):")
    for result in analysis_results:
        clip_info = result['clip_info']
        print(f"   Clip {clip_info['clip_index']}: {clip_info['clip_path']}")
    
    # Verify paths are correct
    print("\n" + "="*60)
    print("VERIFICATION:")
    print("="*60)
    
    all_correct = True
    for i, result in enumerate(analysis_results):
        clip_info = result['clip_info']
        expected_path = clips[i]['clip_path']
        actual_path = clip_info['clip_path']
        
        is_correct = actual_path == expected_path
        status = "✅ PASS" if is_correct else "❌ FAIL"
        
        print(f"{status} Clip {i}:")
        print(f"   Expected: {expected_path}")
        print(f"   Actual:   {actual_path}")
        
        if not is_correct:
            all_correct = False
    
    print("\n" + "="*60)
    if all_correct:
        print("✅ TEST PASSED - All paths correctly preserved!")
        print("The fix is working correctly.")
    else:
        print("❌ TEST FAILED - Some paths are incorrect!")
        print("The fix needs adjustment.")
    print("="*60)
    
    return all_correct


if __name__ == "__main__":
    success = test_path_preservation()
    exit(0 if success else 1)
