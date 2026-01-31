# Getting Started with CineSearch-AI

## Complete Setup Guide

This guide will walk you through setting up and running CineSearch-AI from scratch.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the Application](#running-the-application)
5. [First Time Usage](#first-time-usage)
6. [Common Issues](#common-issues)
7. [Next Steps](#next-steps)

## System Requirements

### Minimum Requirements
- **OS**: Windows 10/11, macOS 10.15+, or Linux
- **Python**: 3.9 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 10GB free space
- **Internet**: Required for downloading models and processing URLs

### Required Software
- **Python 3.9+**: [Download here](https://www.python.org/downloads/)
- **FFmpeg**: [Download here](https://ffmpeg.org/download.html)
- **Git**: [Download here](https://git-scm.com/downloads)

### Optional (for better performance)
- **NVIDIA GPU** with CUDA support (5-8x faster processing)
- **16GB RAM** for processing large videos

## Installation

### Step 1: Install Python

1. Download Python 3.9 or higher from https://www.python.org/downloads/
2. During installation, check "Add Python to PATH"
3. Verify installation:
   ```bash
   python --version
   ```
   Should show: `Python 3.9.x` or higher

### Step 2: Install FFmpeg

**Windows**:
1. Download from https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to System PATH
4. Verify:
   ```bash
   ffmpeg -version
   ```

**macOS** (using Homebrew):
```bash
brew install ffmpeg
```

**Linux** (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install ffmpeg
```

### Step 3: Clone the Repository

```bash
# Clone the project
git clone https://github.com/yourusername/cinesearch-ai.git

# Navigate to project directory
cd cinesearch-ai
```

### Step 4: Create Virtual Environment

**Windows**:
```bash
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate
```

**Linux/macOS**:
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### Step 5: Install Dependencies

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt
```

This will install:
- Streamlit (UI framework)
- YOLO (scene detection)
- Gemini API (video analysis)
- ChromaDB (vector database)
- yt-dlp (video downloading)
- And all other dependencies

**Note**: Installation may take 5-10 minutes depending on your internet speed.

## Configuration

### Step 1: Get Gemini API Key

1. Go to https://aistudio.google.com
2. Sign in with your Google account
3. Click "Get API Key"
4. Create a new API key
5. Copy the key (starts with `AIza...`)

### Step 2: Set Up Environment Variables

**Windows**:
```bash
# Copy example file
copy .env.example .env

# Edit .env file
notepad .env
```

**Linux/macOS**:
```bash
# Copy example file
cp .env.example .env

# Edit .env file
nano .env
# or
vim .env
```

### Step 3: Add Your API Key

Edit the `.env` file and add your Gemini API key:

```env
# Gemini API Key (required)
GEMINI_API_KEY=AIzaSy...your_key_here...

# Optional: OpenAI API Key (for query expansion)
# OPENAI_API_KEY=sk-...your_key_here...
```

Save and close the file.

## Running the Application

### Start the Web Interface

```bash
# Make sure virtual environment is activated
# You should see (venv) in your prompt

# Start Streamlit app
streamlit run app.py
```

The application will automatically open in your browser at:
- **Local**: http://localhost:8501
- **Network**: http://YOUR_IP:8501

### Alternative: Command Line Interface

```bash
# Process a local video
python -m ingestion.pipeline video.mp4

# Process from URL
python -m ingestion.pipeline "https://youtube.com/watch?v=VIDEO_ID"

# With options
python -m ingestion.pipeline video.mp4 --threshold 0.4 --output ./output
```

## First Time Usage

### 1. Initialize the System

When you first open the app:

1. **Go to Settings** (⚙️ icon in sidebar)
2. **Select Engine**: Choose "Gemini 2.5 Pro (Recommended)"
3. **Check API Key**: Should show "API Key Detected ✅"
4. **Initialize Engine**: Click "Initialize / Reload Engine"
5. **Wait**: Takes 10-20 seconds to load models
6. **Confirm**: Should show "Engine Online"

### 2. Process Your First Video

#### Option A: From URL (Recommended for Testing)

1. **Go to Library** (📁 icon in sidebar)
2. **Click "From URL" tab**
3. **Paste a YouTube URL**:
   ```
   https://www.youtube.com/watch?v=dQw4w9WgXcQ
   ```
4. **Click "Process from URL"**
5. **Wait for processing**:
   - Download: 10-30 seconds
   - Processing: 1-3 minutes
   - Total: ~2-4 minutes

6. **Check results**:
   - Success message with video title
   - Number of scenes detected
   - Processing details

#### Option B: Upload Local File

1. **Go to Library** (📁 icon in sidebar)
2. **Click "Upload Files" tab**
3. **Drag and drop** a video file (.mp4, .mov, .avi)
4. **Click "Process Videos"**
5. **Wait for processing**

### 3. Search Your Videos

1. **Go to Home** (🏠 icon in sidebar)
2. **Enter a search query**:
   - "person walking"
   - "car driving on street"
   - "people talking"
3. **Click "Search"**
4. **View results**:
   - Video clips with timestamps
   - Descriptions
   - Relevance scores

### 4. Explore Features

**Advanced Filters**:
- Expand "Advanced Filters"
- Filter by mood, scene type
- Adjust number of results

**Quick Process**:
- Expand "Quick Process Video" on Home
- Paste URL for immediate processing

**Statistics**:
- View in sidebar
- Total scenes indexed
- Number of videos

## Common Issues

### Issue: "GEMINI_API_KEY not set"

**Solution**:
1. Check `.env` file exists
2. Verify API key is correct
3. No spaces around `=` sign
4. Restart the app

### Issue: "FFmpeg not found"

**Solution**:
1. Install FFmpeg (see Step 2 above)
2. Add to system PATH
3. Restart terminal
4. Verify: `ffmpeg -version`

### Issue: "No module named 'streamlit'"

**Solution**:
1. Activate virtual environment
2. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Issue: "Port 8501 already in use"

**Solution**:
```bash
# Use different port
streamlit run app.py --server.port 8502
```

### Issue: "Out of memory"

**Solution**:
1. Process smaller videos
2. Close other applications
3. Disable GPU: Set `use_gpu=False` in code
4. Increase system RAM

### Issue: "Download failed" (URL processing)

**Solution**:
1. Check internet connection
2. Verify URL is accessible
3. Try different URL
4. Install missing packages:
   ```bash
   pip install yt-dlp gdown
   ```

### Issue: "YOLO model not found"

**Solution**:
First run downloads model automatically:
```bash
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

## Next Steps

### Learn More

- **YOLO Integration**: Read `docs/YOLO_INTEGRATION.md`
- **URL Processing**: Read `URL_PROCESSING_GUIDE.md`
- **API Reference**: Read `PROFESSIONAL_SUMMARY.md`
- **Architecture**: Read `docs/ARCHITECTURE.md`

### Test the System

```bash
# Run test suite
python test_yolo_integration.py

# Test with sample video
python test_yolo_integration.py path/to/video.mp4
```

### Process More Videos

1. **Batch Processing**:
   - Upload multiple files at once
   - Process entire folders via CLI

2. **URL Processing**:
   - YouTube playlists
   - Google Drive folders
   - Multiple URLs

3. **Advanced Search**:
   - Use filters
   - Combine queries
   - Export results

### Optimize Performance

1. **Enable GPU**:
   - Install CUDA toolkit
   - Verify: `torch.cuda.is_available()`
   - 5-8x faster processing

2. **Adjust Settings**:
   - Scene detection threshold
   - Sample rate
   - Quality settings

3. **Batch Processing**:
   - Process multiple videos
   - Use command line for automation

## Getting Help

### Documentation

- **README.md**: Project overview
- **docs/**: Detailed documentation
- **YOLO_QUICK_START.md**: YOLO features
- **URL_PROCESSING_GUIDE.md**: URL support

### Troubleshooting

1. Check error messages carefully
2. Review logs in terminal
3. Verify all dependencies installed
4. Check API key is valid
5. Ensure FFmpeg is in PATH

### Community

- GitHub Issues: Report bugs
- Discussions: Ask questions
- Wiki: Additional guides

## Summary Checklist

Before you start, make sure you have:

- [ ] Python 3.9+ installed
- [ ] FFmpeg installed and in PATH
- [ ] Git installed
- [ ] Project cloned
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with GEMINI_API_KEY
- [ ] App running (`streamlit run app.py`)
- [ ] Engine initialized in Settings
- [ ] First video processed successfully

If all items are checked, you're ready to use CineSearch-AI!

## Quick Reference

### Start the App
```bash
cd cinesearch-ai
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
streamlit run app.py
```

### Process Video (CLI)
```bash
python -m ingestion.pipeline "https://youtube.com/watch?v=ID"
```

### Test System
```bash
python test_yolo_integration.py
```

### Stop the App
Press `Ctrl+C` in the terminal

---

**Congratulations!** You're now ready to use CineSearch-AI for semantic video search. Happy searching! 🎬
