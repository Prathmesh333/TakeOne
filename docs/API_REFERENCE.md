# 📖 API Reference

> **Complete API documentation for TakeOne modules**

---

## Table of Contents

- [Scene Detection](#scene-detection)
- [Video Clipper](#video-clipper)
- [Gemini Analyzer](#gemini-analyzer)
- [Vector Search](#vector-search)
- [Configuration](#configuration)

---

## Scene Detection

**Module:** `ingestion/scene_detector.py`

Automatically detects scene boundaries in videos using content-based analysis.

### `detect_scenes()`

Detect scene boundaries in a video file.

```python
from ingestion.scene_detector import detect_scenes

scenes = detect_scenes(
    video_path: str,           # Path to video file
    threshold: float = 27.0,   # Detection sensitivity (lower = more scenes)
    min_scene_len: float = 2.0 # Minimum scene length in seconds
) -> List[Tuple[float, float]]
```

**Returns:** List of `(start_time, end_time)` tuples in seconds.

**Example:**
```python
scenes = detect_scenes("movie.mp4", threshold=25)
# [(0.0, 12.4), (12.4, 28.1), (28.1, 45.6), ...]
```

---

### `detect_scenes_with_details()`

Get detailed scene information including frame numbers.

```python
from ingestion.scene_detector import detect_scenes_with_details

scenes = detect_scenes_with_details(
    video_path: str,
    threshold: float = 27.0
) -> List[dict]
```

**Returns:** List of dicts with:
- `index`: Scene index
- `start_time`: Start time in seconds
- `end_time`: End time in seconds
- `duration`: Duration in seconds
- `start_frame`: Start frame number
- `end_frame`: End frame number

---

### `smart_split_scenes()`

Apply optimization rules to scene list.

```python
from ingestion.scene_detector import smart_split_scenes

optimized = smart_split_scenes(
    scenes: List[Tuple[float, float]],  # Original scene list
    max_duration: float = 10.0,          # Max scene duration before split
    min_duration: float = 2.0            # Min duration before merge
) -> List[Tuple[float, float]]
```

**Rules applied:**
- Scenes > `max_duration` → Subdivided into chunks
- Scenes < `min_duration` → Merged with adjacent

---

## Video Clipper

**Module:** `ingestion/video_clipper.py`

Extract video clips and thumbnails using FFmpeg.

### `extract_clip()`

Extract a single clip from a video.

```python
from ingestion.video_clipper import extract_clip

result = extract_clip(
    video_path: str,     # Source video path
    start_time: float,   # Start time in seconds
    end_time: float,     # End time in seconds
    output_path: str     # Output file path
) -> str | None
```

**Returns:** Path to created clip, or `None` on failure.

---

### `extract_all_clips()`

Extract all scene clips from a video.

```python
from ingestion.video_clipper import extract_all_clips

clips = extract_all_clips(
    video_path: str,                      # Source video
    scenes: List[Tuple[float, float]],    # Scene boundaries
    output_dir: str,                      # Output directory
    video_id: str = None,                 # Video identifier
    max_workers: int = 4                  # Parallel extractions
) -> List[dict]
```

**Returns:** List of clip info dicts:
```python
{
    'clip_index': 0,
    'clip_path': './clips/video_id/scene_0000.mp4',
    'start_time': 0.0,
    'end_time': 8.5,
    'duration': 8.5,
    'video_id': 'video_id',
    'source_video': '/path/to/original.mp4'
}
```

---

### `extract_thumbnail()`

Extract a thumbnail image from video.

```python
from ingestion.video_clipper import extract_thumbnail

result = extract_thumbnail(
    video_path: str,           # Source video
    time_point: float,         # Time in seconds
    output_path: str,          # Output image path
    size: str = "320x180"      # Thumbnail dimensions
) -> str | None
```

---

## Gemini Analyzer

**Module:** `ingestion/gemini_analyzer.py`

Video scene understanding using Gemini 2.5 Pro.

### `GeminiAnalyzer` Class

```python
from ingestion.gemini_analyzer import GeminiAnalyzer

analyzer = GeminiAnalyzer(
    model_name: str = "gemini-2.5-pro",  # Gemini model
    max_concurrent: int = 5,              # Concurrent API requests
    request_delay: float = 0.5            # Delay between requests
)
```

---

### `analyzer.analyze_clip()`

Analyze a single video clip.

```python
result = analyzer.analyze_clip(
    clip_path: str,    # Path to video clip
    retries: int = 3   # Retry attempts on failure
) -> dict
```

**Returns:**
```python
# Success
{
    "status": "success",
    "clip_path": "/path/to/clip.mp4",
    "analysis": {
        "scene_type": "dialogue",
        "description": "...",
        "characters": [...],
        "setting": "...",
        "mood": "...",
        "lighting": "...",
        "camera_work": "...",
        "key_actions": [...],
        "dialogue_summary": "...",
        "tags": [...]
    }
}

# Error
{
    "status": "error",
    "clip_path": "/path/to/clip.mp4",
    "error": "Error message"
}
```

---

### `analyzer.analyze_clips_batch()`

Analyze multiple clips with progress tracking.

```python
results = analyzer.analyze_clips_batch(
    clips: List[dict],                    # List with 'clip_path' key
    progress_callback: Callable = None    # callback(current, total)
) -> List[dict]
```

**Example:**
```python
from tqdm import tqdm

pbar = tqdm(total=len(clips))
def on_progress(current, total):
    pbar.update(1)

results = analyzer.analyze_clips_batch(clips, progress_callback=on_progress)
pbar.close()
```

---

### `analyzer.analyze_video_direct()`

Analyze entire video with timestamped scene breakdown.

```python
result = analyzer.analyze_video_direct(
    video_path: str   # Path to video file
) -> dict
```

**Returns:**
```python
{
    "status": "success",
    "video_path": "/path/to/video.mp4",
    "scenes": [
        {
            "start_time": 0.0,
            "end_time": 5.2,
            "scene_type": "dialogue",
            "description": "...",
            "mood": "...",
            "key_actions": [...],
            "tags": [...]
        },
        ...
    ]
}
```

---

### Convenience Functions

```python
from ingestion.gemini_analyzer import get_analyzer, analyze_clip, analyze_clips

# Get singleton instance
analyzer = get_analyzer()

# Quick single clip analysis
result = analyze_clip("/path/to/clip.mp4")

# Batch analysis
results = analyze_clips(clip_list, progress_callback=on_progress)
```

---

## Vector Search

**Module:** `search/vector_search.py`

ChromaDB-based similarity search for scene retrieval.

### `SceneSearchEngine` Class

```python
from search.vector_search import SceneSearchEngine

engine = SceneSearchEngine(
    collection_name: str = "takeone_scenes",   # ChromaDB collection
    persist_dir: str = "./chroma_db",          # Storage directory
    embedding_model: str = "all-MiniLM-L6-v2"  # Sentence transformer
)
```

---

### `engine.index_scenes()`

Add analyzed scenes to the search index.

```python
engine.index_scenes(
    scenes: List[dict]   # Analyzed scene results from Gemini
) -> int                 # Number of scenes indexed
```

**Scene dict format:**
```python
{
    "clip_info": {
        "clip_index": 0,
        "clip_path": "...",
        "start_time": 0.0,
        "end_time": 5.2,
        "video_id": "movie001",
        "thumbnail_path": "..."
    },
    "analysis": {
        "description": "...",
        "mood": "...",
        "tags": [...]
    }
}
```

---

### `engine.search()`

Search for scenes matching a query.

```python
results = engine.search(
    query: str,              # Natural language query
    top_k: int = 10,         # Number of results
    filters: dict = None     # Optional metadata filters
) -> List[dict]
```

**Returns:**
```python
[
    {
        "id": "movie001_scene_0042",
        "score": 0.89,
        "clip_path": "...",
        "thumbnail_path": "...",
        "start_time": 234.5,
        "end_time": 239.7,
        "video_id": "movie001",
        "description": "...",
        "mood": "tense",
        "scene_type": "dialogue",
        "tags": [...]
    },
    ...
]
```

**Filter examples:**
```python
# Filter by mood
results = engine.search("confrontation scene", filters={"mood": "tense"})

# Filter by scene type
results = engine.search("car", filters={"scene_type": "chase"})
```

---

### `engine.get_stats()`

Get collection statistics.

```python
stats = engine.get_stats() -> dict
# {"total_scenes": 1234, "unique_videos": 20}
```

---

### `engine.delete_video()`

Remove all scenes from a specific video.

```python
deleted = engine.delete_video(
    video_id: str   # Video identifier
) -> int            # Number of scenes deleted
```

---

## Configuration

**File:** `.env`

```env
# Required
GEMINI_API_KEY=your-gemini-api-key

# Optional
OPENAI_API_KEY=your-openai-key          # For Whisper cloud
MAX_CONCURRENT_REQUESTS=5               # Gemini parallel requests
SCENE_DETECTION_THRESHOLD=27            # Scene sensitivity
CHROMA_PERSIST_DIR=./chroma_db          # Vector DB location
```

**File:** `config.py` (optional)

```python
CONFIG = {
    # Scene Detection
    "scene_threshold": 27,
    "min_scene_duration": 2.0,
    "max_scene_duration": 10.0,
    
    # Gemini
    "gemini_model": "gemini-2.5-pro",
    "max_concurrent_requests": 5,
    "request_delay": 0.5,
    
    # Vector Search
    "embedding_model": "all-MiniLM-L6-v2",
    "collection_name": "takeone_scenes",
    "top_k_default": 20,
    
    # Storage
    "clips_dir": "./clips",
    "thumbnails_dir": "./thumbnails",
    "chroma_persist_dir": "./chroma_db"
}
```

---

## Error Handling

All modules use consistent error patterns:

```python
# Function returns None on failure
result = extract_clip(video, start, end, output)
if result is None:
    print("Extraction failed")

# Dict returns with status field
result = analyzer.analyze_clip(clip_path)
if result['status'] == 'error':
    print(f"Analysis failed: {result['error']}")

# Exceptions for critical errors
try:
    scenes = detect_scenes(invalid_path)
except FileNotFoundError:
    print("Video not found")
```

---

## Rate Limits

| Service | Limit | Handling |
|---------|-------|----------|
| Gemini 2.5 Pro | ~1000 RPM | `max_concurrent=5` + `request_delay=0.5` |
| FFmpeg | Disk I/O bound | `max_workers=4` |

---

*TakeOne API Reference v1.0*
