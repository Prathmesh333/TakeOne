"""
Test JSON repair logic for malformed Gemini responses.
"""

import json
import re

def repair_json(json_text):
    """Repair malformed JSON from Gemini responses."""
    json_text_fixed = json_text
    
    # Fix 1: Escape unescaped newlines and special chars
    json_text_fixed = json_text_fixed.replace('\n', '\\n')
    json_text_fixed = json_text_fixed.replace('\r', '\\r')
    json_text_fixed = json_text_fixed.replace('\t', '\\t')
    
    # Fix 2: Remove trailing commas
    json_text_fixed = re.sub(r',(\s*[}\]])', r'\1', json_text_fixed)
    
    try:
        return json.loads(json_text_fixed)
    except json.JSONDecodeError:
        # Try extracting valid JSON portion
        depth = 0
        last_valid_pos = 0
        for i, char in enumerate(json_text_fixed):
            if char == '{' or char == '[':
                depth += 1
            elif char == '}' or char == ']':
                depth -= 1
                if depth == 0:
                    last_valid_pos = i + 1
        
        if last_valid_pos > 0:
            json_text_fixed = json_text_fixed[:last_valid_pos]
            return json.loads(json_text_fixed)
        else:
            raise


def test_json_repair():
    """Test various malformed JSON scenarios."""
    
    print("Testing JSON Repair Logic")
    print("="*60)
    
    # Test 1: Unterminated string with newline
    test1 = '''{
    "scene_type": "dialogue",
    "description": "A person talking
    with a newline in the middle",
    "mood": "casual"
}'''
    
    print("\nTest 1: Unterminated string with newline")
    print("Input:", repr(test1[:50]) + "...")
    try:
        result = repair_json(test1)
        print("✅ PASS - Repaired successfully")
        print("Result:", result.get('description', '')[:50])
    except Exception as e:
        print(f"❌ FAIL - {e}")
    
    # Test 2: Trailing comma
    test2 = '''{
    "scene_type": "action",
    "tags": ["running", "chase",],
    "mood": "tense",
}'''
    
    print("\nTest 2: Trailing commas")
    print("Input:", repr(test2[:50]) + "...")
    try:
        result = repair_json(test2)
        print("✅ PASS - Repaired successfully")
        print("Result:", result.get('scene_type'))
    except Exception as e:
        print(f"❌ FAIL - {e}")
    
    # Test 3: Truncated JSON
    test3 = '''{
    "scene_type": "drama",
    "description": "A complete description",
    "mood": "melancholic",
    "tags": ["sad", "emotional'''
    
    print("\nTest 3: Truncated JSON")
    print("Input:", repr(test3[:50]) + "...")
    try:
        result = repair_json(test3)
        print("✅ PASS - Extracted valid portion")
        print("Result:", result.get('scene_type'))
    except Exception as e:
        print(f"❌ FAIL - {e}")
    
    # Test 4: Tab characters
    test4 = '''{
    "scene_type": "establishing",
    "description": "A scene with	tabs	in it",
    "mood": "peaceful"
}'''
    
    print("\nTest 4: Tab characters")
    print("Input:", repr(test4[:50]) + "...")
    try:
        result = repair_json(test4)
        print("✅ PASS - Repaired successfully")
        print("Result:", result.get('description', '')[:50])
    except Exception as e:
        print(f"❌ FAIL - {e}")
    
    # Test 5: Multiple issues combined
    test5 = '''{
    "scene_type": "action",
    "description": "Multiple
    newlines and	tabs",
    "tags": ["tag1", "tag2",],
    "mood": "intense",
}'''
    
    print("\nTest 5: Multiple issues combined")
    print("Input:", repr(test5[:50]) + "...")
    try:
        result = repair_json(test5)
        print("✅ PASS - Repaired successfully")
        print("Result:", result.get('scene_type'))
    except Exception as e:
        print(f"❌ FAIL - {e}")
    
    print("\n" + "="*60)
    print("JSON Repair Testing Complete")


if __name__ == "__main__":
    test_json_repair()
