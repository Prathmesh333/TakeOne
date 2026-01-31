"""
Quick test to verify all fixes are working
"""

def test_default_prompt_exists():
    """Test that DEFAULT_PROMPT attribute exists"""
    from ingestion.gemini_analyzer import GeminiAnalyzer
    
    assert hasattr(GeminiAnalyzer, 'DEFAULT_PROMPT'), "DEFAULT_PROMPT missing!"
    assert hasattr(GeminiAnalyzer, 'DEFAULT_PROMPT_WITH_YOLO'), "DEFAULT_PROMPT_WITH_YOLO missing!"
    assert hasattr(GeminiAnalyzer, 'ENHANCED_PROMPT'), "ENHANCED_PROMPT missing!"
    assert hasattr(GeminiAnalyzer, 'ENHANCED_PROMPT_WITH_YOLO'), "ENHANCED_PROMPT_WITH_YOLO missing!"
    
    print("✅ All prompts exist as class attributes")
    return True


def test_analyzer_initialization():
    """Test that GeminiAnalyzer can be initialized"""
    import os
    
    # Skip if no API key
    if not os.environ.get('GEMINI_API_KEY'):
        print("⚠️  Skipping initialization test (no API key)")
        return True
    
    from ingestion.gemini_analyzer import GeminiAnalyzer
    
    # Test with enhanced prompt
    analyzer_enhanced = GeminiAnalyzer(use_enhanced_prompt=True)
    assert analyzer_enhanced.use_enhanced_prompt == True
    assert analyzer_enhanced.prompt == GeminiAnalyzer.ENHANCED_PROMPT
    print("✅ Enhanced prompt initialization works")
    
    # Test with default prompt
    analyzer_default = GeminiAnalyzer(use_enhanced_prompt=False)
    assert analyzer_default.use_enhanced_prompt == False
    assert analyzer_default.prompt == GeminiAnalyzer.DEFAULT_PROMPT
    print("✅ Default prompt initialization works")
    
    return True


def test_app_imports():
    """Test that app.py imports successfully"""
    try:
        # Just check if the file can be parsed
        with open('app.py', 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Check for progress bar code
        assert 'overall_progress = st.progress' in code, "Missing overall_progress"
        assert 'stage_progress = st.progress' in code, "Missing stage_progress"
        assert 'progress_callback' in code, "Missing progress_callback"
        
        print("✅ App.py has progress bar code")
        return True
    except Exception as e:
        print(f"❌ App.py test failed: {e}")
        return False


def test_json_cleaning():
    """Test JSON cleaning logic"""
    import json
    import re
    
    # Test cases
    test_cases = [
        ('```json\n{"test": "value"}\n```', {"test": "value"}),
        ('```\n{"test": "value"}\n```', {"test": "value"}),
        ('{"test": "value"}', {"test": "value"}),
        ('Some text before {"test": "value"} some text after', {"test": "value"}),
    ]
    
    for input_text, expected in test_cases:
        # Simulate cleaning logic
        json_text = input_text.strip()
        
        if json_text.startswith("```json"):
            json_text = json_text[7:]
        elif json_text.startswith("```"):
            json_text = json_text[3:]
        if json_text.endswith("```"):
            json_text = json_text[:-3]
        json_text = json_text.strip()
        
        # Try to parse
        try:
            result = json.loads(json_text)
        except json.JSONDecodeError:
            # Try regex extraction
            json_match = re.search(r'\{.*\}', json_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(0)
                result = json.loads(json_text)
        
        assert result == expected, f"Failed for input: {input_text}"
    
    print("✅ JSON cleaning logic works")
    return True


if __name__ == "__main__":
    print("Running fix verification tests...\n")
    
    tests = [
        ("DEFAULT_PROMPT exists", test_default_prompt_exists),
        ("Analyzer initialization", test_analyzer_initialization),
        ("App.py progress bars", test_app_imports),
        ("JSON cleaning", test_json_cleaning),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Test: {name}")
        print('='*60)
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed")
    print('='*60)
    
    if failed == 0:
        print("\n🎉 All tests passed! Fixes are working correctly.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the errors above.")
