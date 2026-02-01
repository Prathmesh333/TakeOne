# TakeOne - Project Structure

Complete overview of the TakeOne project organization.

---

## 📂 Root Directory

```
cinesearch-ai/
├── app.py                          # Main Streamlit UI (START HERE!)
├── app_gradio.py                   # Alternative Gradio UI
├── app_gradio_pro.py               # Gradio Pro UI
├── .env                            # Environment variables (API keys)
├── requirements.txt                # Python dependencies
├── requirements-torch-dependent.txt # PyTorch dependencies
└── yolov8n.pt                      # YOLO model weights
```

---

## 📚 Documentation (User-Facing)

```
├── README.md                       # Main project documentation
├── QUICK_START.md                  # Quick start guide
├── GETTING_STARTED.md              # Detailed usage guide
├── PRESENTATION_CONTENT.md         # Hackathon presentation (10 slides)
├── MULTILINGUAL_FEATURE.md         # Multilingual search docs
├── SCRIPT_SEARCH_EXAMPLES.md       # Script search examples
├── SCRIPT_SEARCH_TEST_GUIDE.md     # Testing guide
├── TEST_VIDEOS_PEXELS.md           # Working test videos
└── TEST_VIDEOS_YOUTUBE.md          # YouTube alternatives
```

**Start with:** `README.md` → `QUICK_START.md` → `TEST_VIDEOS_PEXELS.md`

---

## 🔧 Core Application

### Main Entry Points
```
├── app.py                          # Streamlit UI (recommended)
├── app_gradio.py                   # Gradio UI (alternative)
└── app_gradio_pro.py               # Gradio Pro UI (alternative)
```

### Video Processing Pipeline
```
ingestion/
├── pipeline.py                     # Main orchestrator
├── scene_detector.py               # YOLO scene detection
├── video_clipper.py                # FFmpeg clip extraction
├── frame_extractor.py              # Frame extraction
├── frame_selector.py               # Best frame selection
├── gemini_analyzer.py              # Gemini AI analysis
├── yolo_analyzer.py                # YOLO object detection
├── together_analyzer.py            # Together AI (alternative)
├── embedder.py                     # Vector embeddings
├── video_chunker.py                # Video chunking
└── video_downloader.py             # URL processing (YouTube, etc.)
```

### Search Engine
```
search/
├── vector_search.py                # Semantic search + multilingual
├── script_search.py                # Script-to-sequence matching
└── query_expander.py               # AI query enhancement
```

### Utilities
```
utils/
└── audio.py                        # Audio processing utilities
```

### Database
```
database/
└── __init__.py                     # Database initialization
```

---

## 🧪 Testing & Development

### Test Scripts
```
tests/
├── README.md                       # Testing documentation
├── check_gpu.py                    # GPU/CUDA verification
├── diagnose_gemini.py              # Gemini API testing
├── test_gemini_single.py           # Single image analysis
├── test_gemini_fix.py              # API fix testing
├── test_pipeline.py                # Full pipeline test
├── test_streamlit_pipeline.py      # Streamlit integration test
├── test_yolo_integration.py        # YOLO testing
├── test_multilingual.py            # Multilingual search test
├── test_json_repair.py             # JSON parsing test
├── test_fixes.py                   # Bug fix tests
├── test_path_fix.py                # Path handling test
└── clear_and_reindex.py            # Database reset utility
```

**Run:** `python tests/check_gpu.py` to verify setup

### Installation Scripts
```
scripts/
├── README.md                       # Installation documentation
├── install_ffmpeg_auto.ps1         # FFmpeg auto-installer
├── install_ffmpeg.bat              # FFmpeg manual guide
├── check_ffmpeg.bat                # FFmpeg verification
├── install_pytorch_cuda.bat        # PyTorch + CUDA installer
├── install_requirements_safe.bat   # Safe dependency install
└── run_gradio.bat                  # Launch Gradio UI
```

**Run:** `.\scripts\install_ffmpeg_auto.ps1` for setup

---

## 📖 Technical Documentation

### User Documentation
```
docs/
├── README.md                       # Documentation index
├── ARCHITECTURE.md                 # System architecture
├── API_REFERENCE.md                # API documentation
├── IMPLEMENTATION_GUIDE.md         # Implementation details
├── VIDEO_DOWNLOADER.md             # URL processing guide
├── YOLO_INTEGRATION.md             # YOLO integration docs
└── YOLO_ARCHITECTURE_DIAGRAM.md    # YOLO architecture
```

### Development Documentation (Kiro AI)
```
.kiro/docs/
├── README.md                       # Development docs index
├── NUMBERING_REFERENCE.md          # Doc numbering system
├── 01-60_*.md                      # 60 development progress docs
├── FIX_SUMMARY.md                  # Bug fixes summary
├── HOW_TO_FIX_VIDEO_DISPLAY.md     # Video display fixes
├── ICON_UPDATE_GUIDE.md            # UI icon updates
├── IDEA_SUBMISSION.md              # Hackathon ideas
├── PITCH.md                        # Project pitch
└── SUBMISSION.md                   # Hackathon submission
```

**Note:** `.kiro/docs/` excluded from git (development history)

---

## 💾 Data & Output

### Processed Videos
```
output/
├── clips/                          # Extracted video clips
│   └── [video_name]/              # Clips per video
└── thumbnails/                     # Scene thumbnails
    └── [video_name]/              # Thumbnails per video
```

### Vector Database
```
chroma_db/                          # ChromaDB vector store
├── [collection_id]/               # Collection data
│   ├── data_level0.bin
│   ├── header.bin
│   ├── index_metadata.pickle
│   ├── length.bin
│   └── link_lists.bin
└── chroma.sqlite3                 # SQLite metadata
```

### Database Archives
```
chroma_db_archives/                 # Backup archives
└── chroma_db_archive_[timestamp]/ # Timestamped backups
```

### Test Database
```
test_chroma_db/                     # Test database (isolated)
```

---

## 🎬 Demo & Samples

```
demo/
└── sample_footage/                 # Sample video files (empty)
```

**Note:** Use `TEST_VIDEOS_PEXELS.md` for actual test videos

---

## 🔒 Configuration & Secrets

```
├── .env                            # API keys (NEVER commit!)
├── .env.example                    # Example configuration
└── .gitignore                      # Git ignore rules
```

**Important:** `.env` contains your Gemini API key - keep it secret!

---

## 🗂️ Git & Version Control

```
├── .git/                           # Git repository
└── .gitignore                      # Ignored files/folders
```

### Ignored Items (Not in Git)
- `venv/` - Virtual environment
- `output/` - Processed videos
- `chroma_db/` - Vector database
- `.kiro/docs/` - Development docs
- `.env` - API keys
- `*.mp4`, `*.jpg` - Media files
- `*.pt`, `*.pth` - Model weights
- `__pycache__/` - Python cache

---

## 📊 File Count Summary

| Category | Count | Description |
|----------|-------|-------------|
| Core Python | 15+ | Main application code |
| Test Scripts | 12 | Testing and utilities |
| Install Scripts | 6 | Setup and installation |
| User Docs | 9 | User-facing documentation |
| Technical Docs | 7 | Technical documentation |
| Dev Docs | 68 | Development history (Kiro) |
| **Total** | **117+** | Complete project |

---

## 🚀 Quick Navigation

### For Users
1. **Setup:** `README.md` → `QUICK_START.md`
2. **Testing:** `TEST_VIDEOS_PEXELS.md`
3. **Features:** `MULTILINGUAL_FEATURE.md`, `SCRIPT_SEARCH_EXAMPLES.md`

### For Developers
1. **Architecture:** `docs/ARCHITECTURE.md`
2. **API:** `docs/API_REFERENCE.md`
3. **Testing:** `tests/README.md`
4. **Installation:** `scripts/README.md`

### For Judges (Hackathon)
1. **Overview:** `README.md`
2. **Presentation:** `PRESENTATION_CONTENT.md`
3. **Demo:** `TEST_VIDEOS_PEXELS.md`
4. **Features:** `MULTILINGUAL_FEATURE.md`

---

## 📝 File Naming Conventions

### User Documentation
- `README.md` - Main documentation
- `QUICK_START.md` - Getting started
- `[FEATURE]_FEATURE.md` - Feature documentation
- `TEST_*.md` - Testing guides

### Development Files
- `test_*.py` - Test scripts
- `install_*.bat/ps1` - Installation scripts
- `check_*.py/bat` - Verification scripts
- `diagnose_*.py` - Diagnostic tools

### Code Files
- `app*.py` - Application entry points
- `*_analyzer.py` - Analysis modules
- `*_search.py` - Search modules
- `*_detector.py` - Detection modules

---

## 🎯 Key Files to Know

### Must Read
1. `README.md` - Start here!
2. `QUICK_START.md` - Get running fast
3. `TEST_VIDEOS_PEXELS.md` - Test the app

### For Development
1. `ingestion/pipeline.py` - Main processing logic
2. `search/vector_search.py` - Search implementation
3. `app.py` - UI implementation

### For Troubleshooting
1. `tests/check_gpu.py` - GPU issues
2. `tests/diagnose_gemini.py` - API issues
3. `.kiro/docs/52_ALL_FIXES_SUMMARY.md` - Known fixes

---

## 🔄 Workflow

### User Workflow
```
1. Install (scripts/) → 2. Configure (.env) → 3. Run (app.py) 
→ 4. Upload Video → 5. Search → 6. Export Results
```

### Development Workflow
```
1. Code Change → 2. Test (tests/) → 3. Document (docs/) 
→ 4. Commit (git) → 5. Push (GitHub)
```

### Testing Workflow
```
1. GPU Check (tests/check_gpu.py) → 2. API Check (tests/diagnose_gemini.py)
→ 3. Pipeline Test (tests/test_pipeline.py) → 4. Feature Test (tests/test_*.py)
```

---

**TakeOne - Organized for Success!** 🎬✨

