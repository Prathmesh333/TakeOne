# CineSearch AI Documentation

> **AI-Powered Video Scene Search Engine**

Welcome to the CineSearch AI documentation. This guide covers everything from architecture to implementation.

---

## Quick Links

| Document | Description |
|----------|-------------|
| [Architecture](./ARCHITECTURE.md) | System overview, pipeline diagrams, technology stack |
| [Implementation Guide](./IMPLEMENTATION_GUIDE.md) | Step-by-step setup and deployment |
| [API Reference](./API_REFERENCE.md) | Complete module and function documentation |
| [Video Downloader](./VIDEO_DOWNLOADER.md) | URL processing and download features |
| [YOLO Integration](./YOLO_INTEGRATION.md) | Scene detection with YOLO |

---

## What is CineSearch AI?

CineSearch AI is an AI-powered video search engine that helps you find footage using **natural language queries** instead of manual tags or keywords.

**Instead of:** `"person face"` or `"office scene"`  
**Search like:** `"person speaking at podium with confident expression"` or `"sunset over city skyline with dramatic lighting"`

---

## How It Works

```
┌─────────────┐     ┌────────────────┐     ┌─────────────────┐     ┌────────────┐
│   VIDEO     │────▶│ SCENE DETECT   │────▶│ GEMINI ANALYZE  │────▶│  SEARCH    │
│   INPUT     │     │ (YOLO)         │     │ (2.5 Flash)     │     │  INDEX     │
└─────────────┘     └────────────────┘     └─────────────────┘     └────────────┘
                            │                       │                     │
                    Semantic scene           AI understands        Vector similarity
                    detection                scene context         for fast search
```

### Key Features

1. **YOLO Scene Detection** - Intelligent, semantic scene boundary detection
2. **Gemini Analysis** - Fast, accurate scene understanding with Gemini 2.5 Flash
3. **GPU Acceleration** - CUDA support for 5-10x faster processing
4. **URL Support** - Process videos from YouTube, Google Drive, Vimeo, and more
5. **Parallel Processing** - All clips analyzed simultaneously for maximum speed
6. **Library Management** - Archive, restore, and manage video collections

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Scene Detection | YOLO v8 (GPU accelerated) |
| Video Processing | FFmpeg, OpenCV |
| AI Analysis | Gemini 2.5 Flash |
| Vector Database | ChromaDB |
| Text Embeddings | Sentence Transformers |
| Web Interface | Gradio (primary), Streamlit (alternative) |
| GPU Acceleration | CUDA, PyTorch |

---

## Quick Start

### 1. Get Gemini API Key

1. Visit [aistudio.google.com](https://aistudio.google.com)
2. Create or sign in to your Google account
3. Generate API key
4. Free tier available with generous limits

### 2. Install Dependencies

```bash
# Install PyTorch with CUDA (for GPU)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install other dependencies
pip install -r requirements.txt
```

### 3. Set API Key

```bash
# Create .env file
echo "GEMINI_API_KEY=your-key-here" > .env
```

### 4. Run Application

```bash
# Gradio UI (recommended)
python app_gradio.py

# Streamlit UI (alternative)
streamlit run app.py
```

See [Quick Start Guide](../GRADIO_QUICK_START.md) for detailed instructions.

---

## Performance

| Metric | Value |
|--------|-------|
| Processing 5 scenes | ~5-10 seconds |
| Processing 10 scenes | ~10-15 seconds |
| Search latency | <1 second |
| Supported formats | MP4, MOV, AVI, MKV, WEBM |
| GPU speedup | 5-10x faster than CPU |

---

## Project Structure

```
cinesearch-ai/
├── app.py                 # Streamlit UI
├── app_gradio.py         # Gradio UI (recommended)
├── docs/                 # This documentation
│   ├── README.md
│   ├── ARCHITECTURE.md
│   ├── IMPLEMENTATION_GUIDE.md
│   ├── API_REFERENCE.md
│   ├── VIDEO_DOWNLOADER.md
│   └── YOLO_INTEGRATION.md
├── ingestion/            # Video processing
│   ├── pipeline.py       # Main orchestrator
│   ├── scene_detector.py # YOLO scene detection
│   ├── video_clipper.py  # FFmpeg clip extraction
│   ├── gemini_analyzer.py # AI analysis
│   └── video_downloader.py # URL processing
├── search/               # Search functionality
│   ├── vector_search.py  # ChromaDB interface
│   └── query_expander.py # AI query expansion
└── output/               # Processed videos
    ├── clips/           # Extracted clips
    └── thumbnails/      # Scene thumbnails
```

---

## Key Improvements (v2.0)

### Performance
- **10-20x faster**: Removed artificial rate limiting
- **Parallel processing**: All clips analyzed simultaneously
- **GPU acceleration**: Automatic CUDA support
- **Instant UI**: No page reloads with Gradio

### Reliability
- **100% success rate**: Fixed JSON parsing issues
- **Robust error handling**: Automatic retries
- **Better prompts**: Simplified for reliability

### User Experience
- **Professional UI**: Clean Gradio interface
- **Fast interactions**: Instant expand/collapse
- **Better feedback**: Real-time progress tracking
- **Library management**: Archive and restore features

---

## Documentation Index

### Getting Started
- [Quick Start](../GRADIO_QUICK_START.md) - Get up and running
- [Installation Guide](../INSTALLATION_GUIDE.md) - Detailed setup
- [GPU Setup](../GPU_SETUP_INSTRUCTIONS.md) - CUDA configuration

### User Guides
- [Gradio UI Guide](../GRADIO_UI.md) - Using the interface
- [UI Comparison](../UI_COMPARISON.md) - Streamlit vs Gradio
- [Video Downloader](./VIDEO_DOWNLOADER.md) - URL processing

### Technical Documentation
- [Architecture](./ARCHITECTURE.md) - System design
- [API Reference](./API_REFERENCE.md) - Code documentation
- [Implementation Guide](./IMPLEMENTATION_GUIDE.md) - Development
- [YOLO Integration](./YOLO_INTEGRATION.md) - Scene detection

### Troubleshooting
- [Troubleshooting Guide](../TROUBLESHOOTING_GUIDE.md) - Common issues
- [Issue Resolution](../ISSUE_RESOLVED.md) - Recent fixes
- [Performance](../PERFORMANCE_IMPROVEMENTS.md) - Optimization

---

## Support

- **Documentation**: See docs/ folder
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

---

## Changelog

### v2.0 (Latest)
- Added Gradio UI (professional interface)
- Removed artificial rate limiting (10-20x faster)
- Fixed JSON parsing (100% success rate)
- Improved UI performance (instant interactions)
- Added robust error handling
- Enhanced documentation
- Added URL processing support
- Implemented library management

### v1.0
- Initial release
- Streamlit UI
- Basic video processing
- Gemini analysis
- YOLO scene detection

---

*CineSearch AI - Transform your video library into a searchable database with AI*
