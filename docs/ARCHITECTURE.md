# 🎬 TakeOne - Technical Architecture

> **Semantic Footage Search Engine with Scene-Based AI Analysis**

This document describes the enhanced architecture for TakeOne, utilizing **automatic scene detection** combined with **Gemini 2.5 Pro** for intelligent, context-aware video scene analysis.

---

## 📐 System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           TAKEONE ARCHITECTURE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌──────────┐    ┌──────────────┐    ┌───────────────┐    ┌─────────────┐ │
│   │  VIDEO   │───▶│    SCENE     │───▶│    GEMINI     │───▶│   VECTOR    │ │
│   │  INPUT   │    │  DETECTION   │    │   ANALYSIS    │    │   DATABASE  │ │
│   └──────────┘    └──────────────┘    └───────────────┘    └─────────────┘ │
│                          │                    │                     │       │
│                          ▼                    ▼                     ▼       │
│                   PySceneDetect        Gemini 2.5 Pro          ChromaDB    │
│                   (Local, Free)        (Cloud API)             (Local)     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Processing Pipeline

### Phase 1: Scene Detection (Local - FREE)

**Tool:** PySceneDetect with ContentDetector

The system automatically identifies natural scene boundaries by analyzing frame-to-frame differences:

```
Original Video: movie_clip.mp4 (10 minutes)
════════════════════════════════════════════════════════════════════════════════

Frame Analysis:
├──Frame 1──┤ ≈ ├──Frame 2──┤ ≈ ├──Frame 3──┤ ≠ ├──Frame 4──┤ ...
   (Hero)         (Hero)         (Hero)       (Villain)
                                    ▲
                              SCENE CUT DETECTED!
                        (Large content difference)

Output: Scene boundaries with timestamps
────────────────────────────────────────────────────────────────────────────────
Scene 1:  0.00s -  12.40s  (12.4s)  → Chase sequence
Scene 2: 12.40s -  28.10s  (15.7s)  → Dialogue scene
Scene 3: 28.10s -  45.60s  (17.5s)  → Action sequence
Scene 4: 45.60s -  52.30s   (6.7s)  → Reaction shot
...
```

**Why Scene Detection?**
- Each clip = coherent visual unit
- No awkward mid-action cuts
- Fewer clips to process (80-150 per 10-min video vs 6,000 frames)
- Better semantic understanding for Gemini

---

### Phase 2: Intelligent Clipping (Local - FREE)

**Tool:** FFmpeg

The system applies smart rules to ensure optimal clip lengths:

```
┌─────────────────────────────────────────────────────────────────┐
│                    SMART CLIPPING RULES                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  IF scene duration > 10 seconds:                                │
│     └─▶ Subdivide into 5-second chunks                          │
│                                                                  │
│  IF scene duration < 2 seconds:                                 │
│     └─▶ Merge with adjacent scene                               │
│                                                                  │
│  OTHERWISE:                                                      │
│     └─▶ Keep scene as single clip                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

Example:
─────────────────────────────────────────────────────────────────
Original Scene: 18.5 seconds (too long)
                ▼
Subdivided:
  ├─ Clip 1: 0-5s
  ├─ Clip 2: 5-10s  
  ├─ Clip 3: 10-15s
  └─ Clip 4: 15-18.5s
```

---

### Phase 3: Gemini 2.5 Pro Analysis (Cloud API)

**Tool:** Google Gemini 2.5 Pro with native video understanding

Each clip is uploaded directly to Gemini for comprehensive scene analysis:

```
┌─────────────────────────────────────────────────────────────────┐
│                     GEMINI ANALYSIS OUTPUT                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Input: scene_042.mp4 (5.2 seconds)                             │
│                                                                  │
│  Output:                                                         │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ {                                                        │    │
│  │   "scene_type": "dialogue",                             │    │
│  │   "description": "Intense confrontation between two     │    │
│  │                   men in dimly lit warehouse. Close-up  │    │
│  │                   shots showing facial tension.",        │    │
│  │   "characters": [                                        │    │
│  │     "Middle-aged man in suit (protagonist)",            │    │
│  │     "Younger man in leather jacket (antagonist)"        │    │
│  │   ],                                                     │    │
│  │   "setting": "Industrial warehouse, night",             │    │
│  │   "mood": "tense, confrontational",                     │    │
│  │   "lighting": "low-key, dramatic shadows",              │    │
│  │   "camera_work": "close-ups, shot-reverse-shot",        │    │
│  │   "key_actions": ["stare-down", "fist clenching"],      │    │
│  │   "tags": ["confrontation", "tension", "warehouse",     │    │
│  │            "night", "dramatic", "dialogue", "conflict"] │    │
│  │ }                                                        │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Gemini Prompt Template:**
```
Analyze this video clip for a film search engine. Provide:

1. SCENE_TYPE: (action/dialogue/romance/chase/fight/comedy/drama/transition)
2. DESCRIPTION: 2-3 sentences describing the visual content
3. CHARACTERS: List of people/characters visible with brief descriptions
4. SETTING: Location and environment
5. MOOD: Emotional tone (tense, joyful, melancholic, etc.)
6. LIGHTING: Lighting style (high-key, low-key, natural, etc.)
7. CAMERA_WORK: Shot types and movements
8. KEY_ACTIONS: Important actions or events
9. TAGS: 10-15 searchable keywords

Format as JSON.
```

---

### Phase 4: Vector Embedding & Storage

**Tools:** Sentence Transformers + ChromaDB

```
┌─────────────────────────────────────────────────────────────────┐
│                    VECTOR DATABASE SCHEMA                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Collection: "takeone_scenes"                                   │
│                                                                  │
│  Document:                                                       │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ id: "movie001_scene042"                                  │    │
│  │                                                          │    │
│  │ embedding: [0.23, -0.45, 0.67, ...]  (768-dim)          │    │
│  │            ↑                                             │    │
│  │            Generated from concatenated text:             │    │
│  │            description + mood + tags                     │    │
│  │                                                          │    │
│  │ metadata: {                                              │    │
│  │   "video_id": "movie001",                               │    │
│  │   "video_name": "The_Negotiator.mp4",                   │    │
│  │   "scene_index": 42,                                    │    │
│  │   "start_time": 234.5,                                  │    │
│  │   "end_time": 239.7,                                    │    │
│  │   "duration": 5.2,                                      │    │
│  │   "scene_type": "dialogue",                             │    │
│  │   "mood": "tense",                                      │    │
│  │   "clip_path": "/clips/movie001/scene_042.mp4",         │    │
│  │   "thumbnail_path": "/thumbs/movie001/scene_042.jpg",   │    │
│  │   "full_analysis": { ... }                              │    │
│  │ }                                                        │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔍 Search Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                       SEARCH PIPELINE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  User Query: "romantic sunset beach scene"                      │
│              │                                                   │
│              ▼                                                   │
│  ┌────────────────────────────────────┐                         │
│  │  1. QUERY EMBEDDING                │                         │
│  │     Same model as indexing         │                         │
│  │     → [0.12, 0.89, -0.34, ...]     │                         │
│  └────────────────────────────────────┘                         │
│              │                                                   │
│              ▼                                                   │
│  ┌────────────────────────────────────┐                         │
│  │  2. VECTOR SIMILARITY SEARCH       │                         │
│  │     ChromaDB cosine similarity     │                         │
│  │     Returns top-K matches          │                         │
│  └────────────────────────────────────┘                         │
│              │                                                   │
│              ▼                                                   │
│  ┌────────────────────────────────────┐                         │
│  │  3. OPTIONAL: METADATA FILTERING   │                         │
│  │     Filter by mood, scene_type     │                         │
│  └────────────────────────────────────┘                         │
│              │                                                   │
│              ▼                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  RESULTS                                                    │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │ 1. "Love Story" @ 45:32 - Beach sunset kiss         │  │ │
│  │  │    Similarity: 94%  |  Mood: romantic  |  [▶️ Play]  │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │ 2. "Summer Dreams" @ 1:12:05 - Couple on beach      │  │ │
│  │  │    Similarity: 89%  |  Mood: peaceful  |  [▶️ Play]  │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Performance Estimates

### Processing Time (20 videos × 10 minutes each)

| Stage | Method | Time | Notes |
|-------|--------|------|-------|
| Scene Detection | PySceneDetect | ~5-10 min | Local, parallelizable |
| Clip Extraction | FFmpeg | ~10-15 min | Local, parallelizable |
| Gemini Analysis | API (parallel) | ~30-45 min | 5 concurrent requests |
| Embedding + Storage | Local | ~5 min | Batch processing |
| **Total** | - | **~50-75 min** | For 200 min of footage |

### Cost Analysis

| Item | Rate | Usage | Cost |
|------|------|-------|------|
| Gemini 2.5 Pro (input) | $1.25/1M tokens | ~5M tokens | ~$6.25 |
| Gemini 2.5 Pro (output) | $10/1M tokens | ~500K tokens | ~$5.00 |
| Video upload | Included | - | $0 |
| **Total** | - | - | **~$11-15** |

With **$300 Google Cloud credits**, you can process **~4,000+ minutes of video** (66+ hours).

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Scene Detection** | PySceneDetect | Automatic scene boundary detection |
| **Video Processing** | FFmpeg | Clip extraction, format conversion |
| **VLM Analysis** | Gemini 2.5 Pro | Native video understanding |
| **Text Embeddings** | Sentence Transformers | Query and description embedding |
| **Vector Database** | ChromaDB | Similarity search, metadata storage |
| **Web Interface** | Streamlit | User interface |
| **Audio Transcription** | Whisper | Dialogue search (optional) |

---

## 📁 Module Structure

```
takeone/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── .env                            # API keys (GEMINI_API_KEY)
│
├── ingestion/
│   ├── __init__.py
│   ├── scene_detector.py           # [NEW] PySceneDetect integration
│   ├── video_clipper.py            # [NEW] Smart clip extraction
│   ├── gemini_analyzer.py          # [NEW] Gemini 2.5 video analysis
│   ├── video_chunker.py            # Legacy fixed-duration chunking
│   ├── frame_extractor.py          # Frame extraction utilities
│   └── embedder.py                 # Text embedding generation
│
├── search/
│   ├── __init__.py
│   ├── vector_search.py            # ChromaDB similarity search
│   └── query_expander.py           # Optional LLM query expansion
│
├── database/
│   └── chromadb_client.py          # Vector DB operations
│
├── utils/
│   ├── __init__.py
│   └── audio.py                    # Whisper transcription
│
├── clips/                          # Extracted scene clips
│   └── {video_id}/
│       └── scene_{index}.mp4
│
├── thumbnails/                     # Scene thumbnails
│   └── {video_id}/
│       └── scene_{index}.jpg
│
└── chroma_db/                      # Persistent vector storage
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install scenedetect[opencv] google-generativeai chromadb sentence-transformers streamlit
```

### 2. Set Up API Key

```bash
# Get API key from https://aistudio.google.com
# Or use Google Cloud $300 credits

export GEMINI_API_KEY="your-api-key-here"
```

### 3. Run the Application

```bash
streamlit run app.py
```

---

## 🔧 Configuration Options

```python
# ingestion/config.py

CONFIG = {
    # Scene Detection
    "scene_threshold": 27,           # ContentDetector sensitivity (lower = more scenes)
    "min_scene_duration": 2.0,       # Minimum scene length (seconds)
    "max_scene_duration": 10.0,      # Maximum before subdividing
    
    # Gemini API
    "gemini_model": "gemini-2.5-pro",
    "max_concurrent_requests": 5,    # Rate limit compliance
    "request_delay": 0.5,            # Seconds between requests
    
    # Vector Search
    "embedding_model": "all-MiniLM-L6-v2",
    "top_k_results": 20,
    
    # Storage
    "clips_dir": "./clips",
    "thumbnails_dir": "./thumbnails",
    "chroma_persist_dir": "./chroma_db"
}
```

---

## 📈 Why This Architecture?

| Approach | Clips/10min | API Calls | Time | Quality |
|----------|-------------|-----------|------|---------|
| Frame-by-frame (10fps) | 6,000 | 6,000 | 33+ hrs | Redundant |
| Fixed 2s chunks | 300 | 300 | ~50 min | May split scenes |
| **Scene-based (ours)** | 80-150 | 80-150 | ~30 min | ✅ Best |

**Scene-based wins because:**
1. **Natural boundaries** - Each clip is a coherent unit
2. **Fewer API calls** - 5-10x reduction vs fixed chunks
3. **Better semantics** - Gemini understands complete scenes
4. **Cost efficient** - Lower API costs
5. **Faster processing** - Less data to analyze

---

## 🔮 Future Enhancements

1. **Multi-modal search** - Combine visual + audio + dialogue
2. **Face recognition** - Search by actor/character
3. **Editing integration** - Premiere Pro / DaVinci Resolve plugins
4. **Real-time processing** - Live footage ingestion
5. **Collaborative libraries** - Shared team indexes

---

*TakeOne - Find the shot you're looking for, not the one you tagged.*
