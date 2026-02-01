"""
Quick test to verify Gemini JSON key cleanup fix
"""

import json

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

# Test with malformed JSON (simulating Gemini's output)
malformed_json = {
    '\n    "scene_type"': 'dialogue',
    '\n    "description"': 'A person speaking',
    '\n    "mood"': 'neutral',
    'tags': ['person', 'speaking'],
    'nested': {
        '\n    "key1"': 'value1',
        '\t"key2"': 'value2'
    }
}

print("BEFORE cleanup:")
print(json.dumps(malformed_json, indent=2))
print("\nKeys:", list(malformed_json.keys()))

# Clean it
cleaned = clean_dict_keys(malformed_json)

print("\n" + "="*50)
print("AFTER cleanup:")
print(json.dumps(cleaned, indent=2))
print("\nKeys:", list(cleaned.keys()))

# Test access
print("\n" + "="*50)
print("Testing key access:")
try:
    print(f"scene_type: {cleaned['scene_type']}")
    print(f"description: {cleaned['description']}")
    print(f"mood: {cleaned['mood']}")
    print(f"nested.key1: {cleaned['nested']['key1']}")
    print("\n✅ All keys accessible!")
except KeyError as e:
    print(f"\n❌ KeyError: {e}")
