"""
Comprehensive Gemini API diagnostic script
Tests API connectivity, quota, and analyzes why clips are failing
"""

import os
import sys
import logging
import time
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s:%(name)s:%(message)s'
)

def test_api_key():
    """Test if API key is valid"""
    print("\n" + "="*60)
    print("TEST 1: API Key Validation")
    print("="*60)
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment")
        return False
    
    print(f"✓ API key found: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        genai.configure(api_key=api_key)
        print("✓ API key configured successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to configure API: {e}")
        return False

def test_model_access():
    """Test if we can access the model"""
    print("\n" + "="*60)
    print("TEST 2: Model Access")
    print("="*60)
    
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        print("✓ Model initialized: gemini-2.5-flash")
        return model
    except Exception as e:
        print(f"❌ Failed to initialize model: {e}")
        return None

def test_simple_generation(model):
    """Test simple text generation"""
    print("\n" + "="*60)
    print("TEST 3: Simple Text Generation")
    print("="*60)
    
    try:
        response = model.generate_content("Say 'Hello, World!' in JSON format: {\"message\": \"...\"}")
        print(f"✓ Generation successful")
        print(f"Response: {response.text[:200]}")
        return True
    except Exception as e:
        print(f"❌ Generation failed: {type(e).__name__}: {e}")
        return False

def test_json_mode(model):
    """Test JSON mode generation"""
    print("\n" + "="*60)
    print("TEST 4: JSON Mode Generation")
    print("="*60)
    
    try:
        response = model.generate_content(
            "Return a JSON object with fields: name, age, city",
            generation_config={
                "response_mime_type": "application/json",
                "max_output_tokens": 1024
            }
        )
        print(f"✓ JSON mode successful")
        print(f"Response: {response.text[:200]}")
        
        # Try parsing
        import json
        data = json.loads(response.text)
        print(f"✓ Valid JSON parsed: {list(data.keys())}")
        return True
    except Exception as e:
        print(f"❌ JSON mode failed: {type(e).__name__}: {e}")
        return False

def test_file_upload(model):
    """Test file upload"""
    print("\n" + "="*60)
    print("TEST 5: File Upload")
    print("="*60)
    
    # Find a thumbnail to test with
    output_dir = Path("output/thumbnails")
    if not output_dir.exists():
        print(f"❌ No thumbnails directory found: {output_dir}")
        return False
    
    # Find first thumbnail
    thumbnails = list(output_dir.rglob("*.jpg"))
    if not thumbnails:
        print(f"❌ No thumbnails found in {output_dir}")
        return False
    
    test_thumb = thumbnails[0]
    print(f"Testing with: {test_thumb}")
    print(f"File size: {test_thumb.stat().st_size} bytes")
    
    try:
        # Upload file
        print("Uploading file...")
        img_file = genai.upload_file(str(test_thumb))
        print(f"✓ File uploaded: {img_file.name}")
        print(f"  State: {img_file.state.name}")
        
        # Wait for processing
        max_wait = 30
        waited = 0
        while img_file.state.name == "PROCESSING" and waited < max_wait:
            print(f"  Waiting... ({waited}s)")
            time.sleep(1)
            waited += 1
            img_file = genai.get_file(img_file.name)
        
        print(f"  Final state: {img_file.state.name}")
        
        if img_file.state.name != "ACTIVE":
            print(f"❌ File not active: {img_file.state.name}")
            return False
        
        print("✓ File ready for analysis")
        
        # Try analyzing
        print("\nAnalyzing image...")
        response = model.generate_content(
            ["Describe this image in one sentence.", img_file],
            generation_config={
                "max_output_tokens": 100
            }
        )
        print(f"✓ Analysis successful")
        print(f"Response: {response.text}")
        
        # Cleanup
        genai.delete_file(img_file.name)
        print("✓ File cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ File upload/analysis failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rate_limits(model):
    """Test rate limiting with multiple requests"""
    print("\n" + "="*60)
    print("TEST 6: Rate Limiting (5 rapid requests)")
    print("="*60)
    
    success_count = 0
    for i in range(5):
        try:
            response = model.generate_content(
                f"Say 'Request {i+1}' in JSON: {{\"message\": \"...\"}}",
                generation_config={
                    "response_mime_type": "application/json",
                    "max_output_tokens": 50
                }
            )
            print(f"✓ Request {i+1}/5 successful")
            success_count += 1
            time.sleep(0.5)  # Small delay
        except Exception as e:
            print(f"❌ Request {i+1}/5 failed: {type(e).__name__}: {e}")
    
    print(f"\nRate limit test: {success_count}/5 successful")
    return success_count >= 3  # At least 3/5 should succeed

def main():
    print("\n" + "="*60)
    print("GEMINI API DIAGNOSTIC TOOL")
    print("="*60)
    
    results = {}
    
    # Run tests
    results['api_key'] = test_api_key()
    if not results['api_key']:
        print("\n❌ Cannot proceed without valid API key")
        return
    
    model = test_model_access()
    if not model:
        print("\n❌ Cannot proceed without model access")
        return
    results['model_access'] = True
    
    results['simple_generation'] = test_simple_generation(model)
    results['json_mode'] = test_json_mode(model)
    results['file_upload'] = test_file_upload(model)
    results['rate_limits'] = test_rate_limits(model)
    
    # Summary
    print("\n" + "="*60)
    print("DIAGNOSTIC SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL TESTS PASSED")
        print("\nGemini API is working correctly.")
        print("The issue might be:")
        print("  1. Thumbnail file paths are incorrect")
        print("  2. Too many concurrent requests")
        print("  3. Prompt is too complex")
        print("\nTry running with DEBUG logging to see detailed errors.")
    else:
        print("❌ SOME TESTS FAILED")
        print("\nPlease fix the failing tests before proceeding.")
        print("Common issues:")
        print("  - Invalid API key")
        print("  - API quota exceeded")
        print("  - Network connectivity issues")
        print("  - Model not available in your region")
    print("="*60)

if __name__ == "__main__":
    main()
