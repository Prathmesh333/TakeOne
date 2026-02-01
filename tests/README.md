# Tests & Utilities

This folder contains test scripts and utility tools for TakeOne development and troubleshooting.

## Test Scripts

### GPU & Hardware Tests
- **`check_gpu.py`** - Check if GPU/CUDA is available and working
  ```bash
  python tests/check_gpu.py
  ```

### API & Integration Tests
- **`diagnose_gemini.py`** - Test Gemini API connection and configuration
  ```bash
  python tests/diagnose_gemini.py
  ```

- **`test_gemini_single.py`** - Test Gemini analysis on a single image
  ```bash
  python tests/test_gemini_single.py output/thumbnails/video/scene_0001.jpg
  ```

- **`test_gemini_fix.py`** - Test Gemini API fixes and error handling

### Pipeline Tests
- **`test_pipeline.py`** - Test complete video processing pipeline
  ```bash
  python tests/test_pipeline.py
  ```

- **`test_streamlit_pipeline.py`** - Test Streamlit UI integration

- **`test_yolo_integration.py`** - Test YOLO scene detection
  ```bash
  python tests/test_yolo_integration.py
  python tests/test_yolo_integration.py path/to/video.mp4
  ```

### Feature Tests
- **`test_multilingual.py`** - Test multilingual search functionality
  ```bash
  python tests/test_multilingual.py
  ```

- **`test_json_repair.py`** - Test JSON parsing and repair logic

- **`test_fixes.py`** - Test various bug fixes

- **`test_path_fix.py`** - Test file path handling

## Utility Scripts

### Database Management
- **`clear_and_reindex.py`** - Clear ChromaDB and reindex all videos
  ```bash
  python tests/clear_and_reindex.py
  ```
  **Warning:** This deletes all indexed data!

## Running Tests

### Quick Test Suite
```bash
# Test GPU
python tests/check_gpu.py

# Test Gemini API
python tests/diagnose_gemini.py

# Test pipeline with sample video
python tests/test_pipeline.py

# Test multilingual
python tests/test_multilingual.py
```

### Before Deployment
Run these tests to ensure everything works:
1. `check_gpu.py` - Verify GPU acceleration
2. `diagnose_gemini.py` - Verify API key
3. `test_pipeline.py` - Verify processing works
4. `test_multilingual.py` - Verify search works

## Troubleshooting

### GPU Not Detected
```bash
python tests/check_gpu.py
```
If False, see [GPU Setup Guide](../.kiro/docs/02_GPU_SETUP_INSTRUCTIONS.md)

### API Key Issues
```bash
python tests/diagnose_gemini.py
```
Check `.env` file and API key validity

### Processing Errors
```bash
python tests/test_pipeline.py
```
Check logs for detailed error messages

## Development

When adding new features:
1. Write test script in this folder
2. Name it `test_<feature>.py`
3. Update this README
4. Run test before committing

---

**Note:** These are development/testing tools. End users should use the main `app.py` interface.
