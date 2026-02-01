# TakeOne Documentation

> **AI-Powered Semantic Video Search Engine**

Welcome to TakeOne documentation. Find the perfect shot using natural language, in any language.

---

## 📂 Documentation Sections

### 🚀 [User Guides](guides/) - Get Started
- [Quick Start](guides/QUICK_START.md) ⭐ - 5-minute setup
- [Getting Started](guides/GETTING_STARTED.md) - Complete guide
- [Multilingual Search](guides/MULTILINGUAL_FEATURE.md) - Any language

### 🧪 [Testing & Examples](testing/) - Try It Out
- [Test Videos](testing/TEST_VIDEOS_PEXELS.md) ⭐ - Working test videos
- [Script Examples](testing/SCRIPT_SEARCH_EXAMPLES.md) - Script search
- [Test Guide](testing/SCRIPT_SEARCH_TEST_GUIDE.md) - Testing guide

### 🏆 [Hackathon Materials](hackathon/) - For Judges
- [Presentation](hackathon/PRESENTATION_CONTENT.md) ⭐ - 10-slide deck
- [Project Structure](hackathon/PROJECT_STRUCTURE.md) - File organization

---

## 🚀 Quick Links

| Document | Description |
|----------|-------------|
| [Architecture](./ARCHITECTURE.md) | System design and pipeline |
| [Implementation Guide](./IMPLEMENTATION_GUIDE.md) | Setup and deployment |
| [API Reference](./API_REFERENCE.md) | Module documentation |
| [Video Downloader](./VIDEO_DOWNLOADER.md) | URL processing features |
| [YOLO Integration](./YOLO_INTEGRATION.md) | Scene detection |

---

## What is TakeOne?

TakeOne is an AI-powered video search engine that lets you find footage using **natural language queries** in **any language**.

**Search like a human:**
- "person walking past a car" 
- "व्यक्ति कार के पास चल रहा है" (Hindi)
- "sunset over city with dramatic lighting"
- "worried person checking phone"

---

## ✨ Key Features

### 🌐 Multilingual Search
- **Type in ANY language** - Hindi, Tamil, Telugu, Spanish, French, Chinese, etc.
- **Automatic translation** - AI translates to English automatically
- **Query enhancement** - Generates 10+ variations for better results
- **Zero configuration** - Works out of the box

### 🎬 Script-to-Sequence Search
- **Paste entire scripts** - Multiple actions in sequence
- **Sequential results** - Footage returned in script order (Action 1 → 2 → 3...)
- **Perfect for editing** - Ready-to-use edit sequences
- **Export options** - CSV, text, JSON formats

### 🎯 Intelligent Scene Detection
- **YOLO-powered** - Semantic scene boundary detection
- **GPU accelerated** - 5-10x faster with CUDA
- **Smart clipping** - Optimal clip lengths (2-10 seconds)
- **No mid-action cuts** - Coherent visual units

### 🤖 AI-Powered Analysis
- **Gemini 2.5 Flash** - Fast, accurate scene understanding
- **Comprehensive metadata** - Scene type, mood, lighting, camera work
- **Named entities** - People, locations, objects, vehicles
- **Searchable tags** - 10-15 keywords per scene

### 📚 Library Management
- **Multiple libraries** - Organize by project
- **Archive & restore** - Timestamped backups
- **Switch libraries** - Easy project switching
- **Statistics** - Track indexed content

### 🌐 URL Support
- **YouTube** - Direct video processing
- **Google Drive** - Shared links
- **Vimeo, Dailymotion** - Multiple platforms
- **Direct URLs** - Any accessible video

---

## 🏗️ Architecture

```
┌─────────────┐     ┌────────────────┐     ┌─────────────────┐     ┌────────────┐
│   VIDEO     │────▶│ SCENE DETECT   │────▶│ GEMINI ANALYZE  │────▶│  SEARCH    │
│   INPUT     │     │ (YOLO)         │     │ (2.5 Flash)     │     │  INDEX     │
└─────────────┘     └────────────────┘     └─────────────────┘     └────────────┘
                            │                       │                     │
                    Semantic scene           AI understands        Vector similarity
                    detection                scene context         for fast search
```

### Processing Pipeline

1. **Scene Detection** - YOLO identifies natural scene boundaries
2. **Smart Clipping** - FFmpeg extracts optimal-length clips
3. **AI Analysis** - Gemini analyzes each scene comprehensively
4. **Vector Embedding** - Sentence Transformers create searchable embeddings
5. **Storage** - ChromaDB stores vectors and metadata

### Search Pipeline

1. **Translation** - Any language → English (if needed)
2. **Query Enhancement** - AI generates 10+ query variations
3. **Vector Search** - Find similar scenes using embeddings
4. **Results** - Ranked by relevance with full metadata

---

## 💻 Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Scene Detection** | YOLO v8 | Semantic boundary detection |
| **Video Processing** | FFmpeg, OpenCV | Clip extraction, thumbnails |
| **AI Analysis** | Gemini 2.5 Flash | Scene understanding |
| **Translation** | Gemini 2.5 Flash | Multilingual support |
| **Text Embeddings** | Sentence Transformers | Vector search |
| **Vector Database** | ChromaDB | Similarity search |
| **Web Interface** | Streamlit | User interface |
| **GPU Acceleration** | CUDA, PyTorch | 5-10x speedup |

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| Scene detection | ~1-2 seconds per minute of video |
| AI analysis | ~5-10 seconds for 5 scenes (parallel) |
| Search latency | <1 second |
| Translation | ~200-500ms per query |
| Query enhancement | ~500-800ms |
| GPU speedup | 5-10x faster than CPU |
| Supported formats | MP4, MOV, AVI, MKV, WEBM |

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8+
- FFmpeg installed
- CUDA-capable GPU (optional, for acceleration)
- Gemini API key

### 2. Get Gemini API Key

1. Visit [aistudio.google.com](https://aistudio.google.com)
2. Sign in with Google account
3. Generate API key
4. Free tier: Generous limits

### 3. Installation

```bash
# Clone repository
git clone https://github.com/Prathmesh333/TakeOne-Final.git
cd cinesearch-ai

# Install PyTorch with CUDA (for GPU)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install dependencies
pip install -r requirements.txt

# Set API key
echo "GEMINI_API_KEY=your-key-here" > .env
```

### 4. Run Application

```bash
streamlit run app.py
```

Open browser to `http://localhost:8501`

---

## 📁 Project Structure

```
cinesearch-ai/
├── app.py                      # Streamlit UI (main interface)
├── docs/                       # Documentation
│   ├── README.md              # This file
│   ├── ARCHITECTURE.md        # System design
│   ├── IMPLEMENTATION_GUIDE.md
│   ├── API_REFERENCE.md
│   ├── VIDEO_DOWNLOADER.md
│   └── YOLO_INTEGRATION.md
├── ingestion/                  # Video processing pipeline
│   ├── pipeline.py            # Main orchestrator
│   ├── scene_detector.py      # YOLO scene detection
│   ├── video_clipper.py       # FFmpeg clip extraction
│   ├── gemini_analyzer.py     # AI analysis + translation
│   ├── video_downloader.py    # URL processing
│   └── embedder.py            # Text embeddings
├── search/                     # Search functionality
│   ├── vector_search.py       # ChromaDB + translation
│   ├── script_search.py       # Script-to-sequence search
│   └── query_expander.py      # AI query enhancement
├── output/                     # Processed videos
│   ├── clips/                 # Extracted scene clips
│   └── thumbnails/            # Scene thumbnails
├── chroma_db/                  # Vector database
└── chroma_db_archives/         # Library backups
```

---

## 🎨 UI Features

### Cinema Color Palette
- **Deep Slate** (#0D1117) - Professional dark background
- **Electric Cyan** (#00E5FF) - AI glow, accents
- **Cinema Rust** (#E64A19) - Action, highlights
- **High-Key White** (#F0F6FC) - Text, clarity

### Search Modes

**Quick Search**
- Single query search
- Instant results
- Advanced filters (mood, scene type)
- Expandable result cards

**Script Sequence Search**
- Multi-action scripts
- Sequential results (Action 1 → 2 → 3...)
- Export edit sequences
- Perfect for video editing workflow

### Library Management
- Create/switch libraries
- Archive with timestamps
- Restore from backups
- View statistics

---

## 🌍 Multilingual Support

### Supported Languages

**Indian Languages:**
- Hindi (हिंदी)
- Tamil (தமிழ்)
- Telugu (తెలుగు)
- Marathi (मराठी)
- Kannada (ಕನ್ನಡ)
- Bengali (বাংলা)
- Gujarati (ગુજરાતી)
- Malayalam (മലയാളം)
- Punjabi (ਪੰਜਾਬੀ)
- Urdu (اردو)

**Other Languages:**
- Spanish, French, German, Italian, Portuguese
- Chinese (中文), Japanese (日本語), Korean (한국어)
- Arabic (العربية), Hebrew (עברית), Persian (فارسی)
- And many more...

### How It Works

```
User Query (Any Language)
    ↓
Translation → English
    ↓
AI Query Enhancement → 10+ Variations
    ↓
Vector Search → Matching Footage
```

---

## 📖 Usage Examples

### Quick Search

```
English: "person walking past a car"
Hindi: "व्यक्ति कार के पास चल रहा है"
Tamil: "ஒரு நபர் காரை கடந்து நடக்கிறார்"
```

All return the same results!

### Script Search

```
Input (Hindi):
एक व्यक्ति व्यस्त शहर की सड़क पर चिंतित दिख रहा है।
वे रुकते हैं और चिंतित चेहरे के साथ अपना फोन देखते हैं।
फोन स्क्रीन पर एक संदेश दिखाई देता है।

Output:
Action 1: Person looking worried on busy street → 3 footage options
Action 2: Person checking phone with concerned expression → 3 options
Action 3: Close-up of phone screen showing message → 3 options
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Required
GEMINI_API_KEY=your_api_key_here

# Optional
CUDA_VISIBLE_DEVICES=0  # GPU selection
```

### Search Settings

```python
# In search calls
auto_translate=True          # Enable multilingual
use_query_expansion=True     # AI enhancement
top_k=10                     # Number of results
```

---

## 📈 Recent Updates

### v3.0 (Latest)
- ✅ Multilingual search (all languages)
- ✅ Script-to-sequence search
- ✅ Cinema color palette
- ✅ JSON parsing fixes (100% reliability)
- ✅ Video display fixes
- ✅ Enhanced UI with proper icons
- ✅ Library management
- ✅ URL processing

### v2.0
- Professional Streamlit UI
- YOLO scene detection
- Gemini 2.5 Flash integration
- GPU acceleration
- Parallel processing

### v1.0
- Initial release
- Basic video processing
- Simple search

---

## 🐛 Troubleshooting

### Common Issues

**Video not playing:**
- Run `python clear_and_reindex.py` to fix database
- Check clip paths in database

**Slow processing:**
- Enable GPU acceleration
- Check CUDA installation: `python check_gpu.py`

**Translation not working:**
- Verify GEMINI_API_KEY in .env
- Check API quota

**Search returns no results:**
- Index videos first
- Check database has content

---

## 📚 Additional Resources

### Documentation
- [Quick Start Guide](../QUICK_START.md)
- [Getting Started](../GETTING_STARTED.md)
- [Multilingual Feature](../MULTILINGUAL_FEATURE.md)
- [Script Search Guide](../SCRIPT_SEARCH_TEST_GUIDE.md)

### Development
- [Kiro Docs](../kiro_docs/) - Development history
- [API Reference](./API_REFERENCE.md) - Code documentation
- [Architecture](./ARCHITECTURE.md) - System design

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Make changes
4. Submit pull request

---

## 📄 License

See LICENSE file for details.

---

## 🙏 Acknowledgments

- Google Gemini for AI capabilities
- Ultralytics for YOLO
- Streamlit for UI framework
- ChromaDB for vector search

---

**TakeOne** - Find the perfect shot, in any language.

*Built for filmmakers, by filmmakers.*
