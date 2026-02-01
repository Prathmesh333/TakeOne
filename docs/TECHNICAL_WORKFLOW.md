# TakeOne - Complete Technical Workflow

**Deep Dive: How TakeOne Transforms Video into Searchable Intelligence**

---

## Architecture Overview

TakeOne is not just a video search engine - it's an intelligent video understanding system that replaces manual video editing workflows with AI-driven semantic analysis. The system uses a multi-stage pipeline where each component serves a specific purpose in transforming raw video into searchable, semantically-rich content.

**Key Innovation:** YOLO acts as the "semantic decision-maker" that governs the entire pipeline, replacing human editors in determining scene boundaries based on content understanding rather than pixel changes.

---

## Stage 1: Semantic Scene Detection (The "Intelligent Cutter")

### Purpose
Automatically identify natural scene boundaries in video without relying on pixel-based methods (like PySceneDetect). Instead of detecting color changes, we detect **concept changes**.

### How YOLO Works as the Scene Detector

**Traditional Approach (PySceneDetect):**
- Analyzes pixel color changes
- Detects cuts, fades, dissolves
- Problem: Misses semantic boundaries (e.g., camera stays on same person but context changes)

**TakeOne's YOLO Approach:**
- Analyzes **semantic content** (objects, people, context)
- Detects **concept changes** (person → car, indoor → outdoor)
- Result: Natural, meaningful scene boundaries

### Technical Implementation

#### Step 1: Frame Sampling
```python
# From scene_detector.py
sample_interval = 5  # Sample every 5th frame for speed
frames = extract_frames_at_interval(video_path, sample_interval)
```

**Why every 5th frame?**
- Balance between accuracy and speed
- At 30fps, this is 6 samples per second
- Sufficient to catch scene changes without processing every frame

#### Step 2: YOLO Inference
```python
# YOLO processes each sampled frame
results = yolo_model(frame)
detections = results[0].boxes
```

**YOLO Output:**
- **Classes:** Object types detected (person, car, cup, phone, etc.)
- **Bounding Boxes:** (x1, y1, x2, y2) coordinates
- **Confidence Scores:** How certain YOLO is about each detection

#### Step 3: Semantic Signature Creation

This is where the magic happens. We convert YOLO's raw output into a mathematical "fingerprint" of the scene.

**Components of the Signature:**

1. **Object Classes (What)**
   ```python
   classes = {person, cup, table}  # Set of detected objects
   ```

2. **Spatial Distribution (Where)**
   ```python
   # Divide frame into 3x3 grid
   grid = [
       [top-left, top-center, top-right],
       [mid-left, mid-center, mid-right],
       [bot-left, bot-center, bot-right]
   ]
   
   # Map each detection to grid cell
   spatial_signature = {
       'person': 'center-middle',
       'cup': 'center-right',
       'table': 'bottom-center'
   }
   ```

3. **Object Counts (How Many)**
   ```python
   counts = {
       'person': 2,
       'cup': 1,
       'table': 1
   }
   ```

**Complete Semantic Signature:**
```python
signature_frame_N = {
    'classes': {'person', 'cup', 'table'},
    'spatial': {'person': 'center', 'cup': 'right', 'table': 'bottom'},
    'counts': {'person': 2, 'cup': 1, 'table': 1}
}
```

#### Step 4: Similarity Calculation (The Math)

Compare Frame N with Frame N-5 (previous sample):

```python
def calculate_similarity(sig1, sig2):
    # 1. Class Similarity (Jaccard Index)
    intersection = sig1['classes'] & sig2['classes']
    union = sig1['classes'] | sig2['classes']
    class_sim = len(intersection) / len(union) if union else 0
    
    # 2. Spatial Similarity
    spatial_matches = sum(
        1 for obj in intersection 
        if sig1['spatial'][obj] == sig2['spatial'][obj]
    )
    spatial_sim = spatial_matches / len(intersection) if intersection else 0
    
    # 3. Count Similarity
    count_diff = sum(
        abs(sig1['counts'].get(obj, 0) - sig2['counts'].get(obj, 0))
        for obj in union
    )
    count_sim = 1 / (1 + count_diff)
    
    # Weighted combination
    similarity = (
        0.5 * class_sim +      # What objects are present
        0.3 * spatial_sim +    # Where they are
        0.2 * count_sim        # How many there are
    )
    
    return similarity
```

#### Step 5: Scene Boundary Decision

```python
threshold = 0.4  # Configurable

if similarity < threshold:
    # Significant semantic change detected
    scene_boundaries.append(current_frame_number)
    logger.info(f"Scene boundary at frame {current_frame_number}")
    logger.info(f"  Previous: {sig1['classes']}")
    logger.info(f"  Current: {sig2['classes']}")
    logger.info(f"  Similarity: {similarity:.2f}")
```

**Example Scene Change:**
```
Frame 100: {person, cup, table} in center → Similarity: 0.95 (same scene)
Frame 105: {person, cup, table} in center → Similarity: 0.93 (same scene)
Frame 110: {car, road, building} in center → Similarity: 0.15 (NEW SCENE!)
```

**Why This Works:**
- Detects semantic changes (person → car) not just visual changes
- Ignores minor movements (person shifts slightly)
- Captures context changes (indoor → outdoor)
- Natural, meaningful boundaries for video editing

---

## Stage 2: Clip Extraction (The "Precision Cutter")

### Purpose
Extract video clips at the exact scene boundaries identified by YOLO, creating coherent visual units.

### Technical Implementation

```python
# From video_clipper.py
def extract_clip(video_path, start_time, end_time, output_path):
    """
    Use FFmpeg to extract clip with frame-accurate precision
    """
    command = [
        'ffmpeg',
        '-ss', str(start_time),           # Start time
        '-i', video_path,                 # Input video
        '-t', str(end_time - start_time), # Duration
        '-c:v', 'libx264',                # Video codec
        '-c:a', 'aac',                    # Audio codec
        '-avoid_negative_ts', 'make_zero',
        '-y',                             # Overwrite
        output_path
    ]
    subprocess.run(command, capture_output=True)
```

**Key Features:**
- Frame-accurate cutting (no frame loss)
- Preserves video quality
- Maintains audio sync
- Fast processing (hardware acceleration when available)

**Output:**
```
output/clips/video_name/
├── scene_0001.mp4  (0.0s - 3.2s)
├── scene_0002.mp4  (3.2s - 7.8s)
├── scene_0003.mp4  (7.8s - 12.1s)
└── ...
```

---

## Stage 3: Thumbnail Extraction (The "Visual Selector")

### Purpose
Select the most representative frame from each clip for preview and analysis.

### Technical Implementation

```python
# From frame_selector.py
def select_best_frame(clip_path):
    """
    Select middle frame as most representative
    (avoids transition artifacts at start/end)
    """
    cap = cv2.VideoCapture(clip_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    middle_frame = total_frames // 2
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame)
    ret, frame = cap.read()
    
    return frame
```

**Why Middle Frame?**
- Avoids transition artifacts
- Most stable composition
- Best represents scene content
- Optimal for AI analysis

---

## Stage 4: YOLO Object Analysis (The "Content Cataloger")

### Purpose
Perform detailed object detection on the selected thumbnail to catalog all visible elements.

### Technical Implementation

```python
# From yolo_analyzer.py
def analyze_frame(frame):
    """
    Comprehensive object detection and spatial analysis
    """
    results = yolo_model(frame)
    
    analysis = {
        'objects': [],
        'spatial_distribution': {},
        'dominant_objects': [],
        'scene_complexity': 0
    }
    
    for detection in results[0].boxes:
        obj = {
            'class': class_names[int(detection.cls)],
            'confidence': float(detection.conf),
            'bbox': detection.xyxy[0].tolist(),
            'position': calculate_grid_position(detection.xyxy[0])
        }
        analysis['objects'].append(obj)
    
    # Calculate scene complexity
    analysis['scene_complexity'] = len(set(obj['class'] for obj in analysis['objects']))
    
    # Identify dominant objects (largest bounding boxes)
    analysis['dominant_objects'] = sorted(
        analysis['objects'],
        key=lambda x: calculate_bbox_area(x['bbox']),
        reverse=True
    )[:3]
    
    return analysis
```

**Output Example:**
```json
{
    "objects": [
        {"class": "person", "confidence": 0.95, "position": "center"},
        {"class": "cup", "confidence": 0.87, "position": "right"},
        {"class": "table", "confidence": 0.92, "position": "bottom"}
    ],
    "dominant_objects": ["person", "table", "cup"],
    "scene_complexity": 3
}
```

---

## Stage 5: Gemini AI Analysis (The "Semantic Interpreter")

### Purpose
Transform visual data into rich, searchable semantic descriptions using Google's Gemini 2.5 Flash.

### Why Gemini After YOLO?

**YOLO provides:** "person, cup, table"  
**Gemini provides:** "A person sits at a wooden table, holding a white ceramic coffee cup. Morning light streams through a window. The atmosphere is calm and contemplative."

### Technical Implementation

```python
# From gemini_analyzer.py
def analyze_scene(thumbnail_path, yolo_data):
    """
    Deep semantic analysis using Gemini 2.5 Flash
    """
    # Load image
    image = PIL.Image.open(thumbnail_path)
    
    # Construct context-aware prompt
    prompt = f"""Analyze this video scene frame in detail.

YOLO detected these objects: {', '.join(yolo_data['dominant_objects'])}

Provide a comprehensive analysis:

1. DESCRIPTION: Detailed visual description (2-3 sentences)
2. SCENE_TYPE: Category (e.g., dialogue, action, establishing, transition)
3. MOOD: Emotional tone (e.g., tense, peaceful, energetic)
4. LIGHTING: Lighting conditions (e.g., natural daylight, dim interior, dramatic)
5. CAMERA: Camera work (e.g., close-up, wide shot, medium shot)
6. SETTING: Location/environment (e.g., office, outdoor park, city street)
7. SUBJECTS: Main subjects and their actions
8. TAGS: 10-15 searchable keywords

Return as JSON."""

    response = gemini_model.generate_content(
        [prompt, image],
        generation_config={
            "temperature": 0.3,  # Lower = more consistent
            "max_output_tokens": 2048,
            "response_mime_type": "application/json"
        }
    )
    
    return json.loads(response.text)
```

**Gemini Output Example:**
```json
{
    "description": "A professional woman in business attire sits at a modern office desk, focused on her laptop screen. The workspace is minimalist with natural light from large windows. A white coffee cup sits beside the laptop.",
    "scene_type": "dialogue",
    "mood": "focused, professional",
    "lighting": "natural daylight, soft",
    "camera": "medium shot",
    "setting": "modern office interior",
    "subjects": ["woman working", "laptop", "desk setup"],
    "tags": ["office", "professional", "working", "laptop", "desk", "business", "woman", "focused", "modern", "workspace", "coffee", "natural light", "interior", "corporate", "productivity"]
}
```

### Parallel Processing Optimization

```python
# Process multiple scenes simultaneously
import concurrent.futures

def analyze_all_scenes(scenes):
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(analyze_scene, scene['thumbnail'], scene['yolo'])
            for scene in scenes
        ]
        results = [f.result() for f in futures]
    return results
```

**Performance:**
- 5 scenes analyzed in parallel
- ~5-10 seconds total (vs 25-50 seconds sequential)
- No artificial rate limiting
- Gemini API handles concurrency

---

## Stage 6: Vector Embedding (The "Semantic Encoder")

### Purpose
Convert text descriptions into mathematical vectors for similarity search.

### Technical Implementation

```python
# From embedder.py
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def create_embedding(text):
    """
    Convert text to 384-dimensional vector
    """
    # Combine all searchable text
    combined_text = f"{description} {scene_type} {mood} {' '.join(tags)}"
    
    # Generate embedding
    embedding = model.encode(combined_text, convert_to_tensor=False)
    
    return embedding.tolist()  # 384-dimensional vector
```

**How It Works:**
- Input: "A person sits at a table with coffee, morning light, calm atmosphere"
- Output: [0.23, -0.45, 0.67, ..., 0.12] (384 numbers)

**Why Vectors?**
- Captures semantic meaning
- Similar concepts → similar vectors
- Enables fast similarity search
- Language-independent (after translation)

---

## Stage 7: ChromaDB Indexing (The "Semantic Database")

### Purpose
Store vectors and metadata for fast similarity search.

### Technical Implementation

```python
# From vector_search.py
import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(
    name="video_scenes",
    metadata={"hnsw:space": "cosine"}  # Cosine similarity
)

def index_scene(scene_data):
    """
    Store scene in vector database
    """
    collection.add(
        ids=[scene_data['id']],
        embeddings=[scene_data['embedding']],
        metadatas=[{
            'clip_path': scene_data['clip_path'],
            'thumbnail_path': scene_data['thumbnail_path'],
            'description': scene_data['description'],
            'scene_type': scene_data['scene_type'],
            'mood': scene_data['mood'],
            'tags': json.dumps(scene_data['tags']),
            'start_time': scene_data['start_time'],
            'end_time': scene_data['end_time'],
            'duration': scene_data['duration']
        }]
    )
```

**ChromaDB Features:**
- HNSW algorithm for fast approximate nearest neighbor search
- Cosine similarity for semantic matching
- Persistent storage (survives restarts)
- Efficient for millions of vectors

---

## Stage 8: Multilingual Search (The "Universal Translator")

### Purpose
Enable search in any language by translating queries to English before searching.

### Processing Pipeline

```
User Query (Any Language)
    ↓
Translation → English (Gemini)
    ↓
Query Enhancement → 10+ Variations (Gemini)
    ↓
Vector Embedding → 384D Vector
    ↓
Similarity Search → Matching Scenes
    ↓
Results (Ranked by Relevance)
```

### Technical Implementation

#### Step 1: Translation
```python
def translate_to_english(query):
    """
    Translate any language to English using Gemini
    """
    prompt = f"""Translate this search query to English. If already English, return as-is.

Query: {query}

Return ONLY the English translation, no explanation."""

    response = gemini_model.generate_content(prompt)
    return response.text.strip()
```

**Example:**
- Input: "कप में कॉफी डाली जा रही है" (Hindi)
- Output: "coffee being poured into cup"

#### Step 2: Query Enhancement
```python
def enhance_query(query):
    """
    Generate multiple query variations for better recall
    """
    prompt = f"""Generate 10 search query variations for: "{query}"

Include:
- Synonyms (e.g., "person" → "man", "woman", "individual")
- Related concepts (e.g., "coffee" → "beverage", "drink", "caffeine")
- Different phrasings (e.g., "pouring coffee" → "coffee being poured")
- Context additions (e.g., "cup" → "ceramic cup", "coffee mug")

Return as JSON array."""

    response = gemini_model.generate_content(prompt)
    variations = json.loads(response.text)
    return variations
```

**Example Output:**
```json
[
    "coffee being poured into cup",
    "pouring hot coffee into mug",
    "filling cup with coffee",
    "coffee stream into ceramic cup",
    "beverage being poured",
    "hot drink preparation",
    "coffee cup filling",
    "pouring liquid into cup",
    "coffee service",
    "preparing hot beverage"
]
```

#### Step 3: Multi-Query Search
```python
def search_with_variations(variations, top_k=10):
    """
    Search with all variations and combine results
    """
    all_results = []
    
    for variation in variations:
        # Embed query
        query_vector = model.encode(variation)
        
        # Search
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=top_k
        )
        
        all_results.extend(results)
    
    # Deduplicate and re-rank
    unique_results = deduplicate_by_id(all_results)
    ranked_results = rank_by_relevance(unique_results)
    
    return ranked_results[:top_k]
```

---

## Stage 9: Script-to-Sequence Search (The "Narrative Matcher")

### Purpose
Match entire scripts to video sequences, returning multiple options per action.

### Processing Pipeline

```
Multi-Line Script (Any Language)
    ↓
Translation → English Script (Gemini)
    ↓
Script Parsing → Sequential Actions (Gemini)
    ↓
For Each Action:
    ├─ Query Enhancement → Variations (Gemini)
    ├─ Vector Search → Top 3 Matches
    └─ Results with Sequence Number
    ↓
Sequential Results (Action 1 → 2 → 3...)
```

### Technical Implementation

#### Step 1: Script Translation
```python
def translate_script(script):
    """
    Translate entire script to English
    """
    prompt = f"""Translate this film script to English:

{script}

Preserve:
- Line breaks
- Sequential structure
- Visual actions

Return ONLY the English translation."""

    response = gemini_model.generate_content(prompt)
    return response.text
```

#### Step 2: Script Parsing
```python
def parse_script_to_actions(script):
    """
    Break script into sequential searchable actions
    """
    prompt = f"""Parse this script into sequential actions:

{script}

Return JSON array:
[
  {{"sequence": 1, "action": "person walking down street", "description": "establishing shot"}},
  {{"sequence": 2, "action": "close-up worried face", "description": "emotional reaction"}},
  ...
]

Focus on visual, searchable elements."""

    response = gemini_model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"}
    )
    
    return json.loads(response.text)
```

**Example:**
```
Input Script:
"A person walks down a busy street.
They stop and check their phone.
Close-up of phone screen showing a message."

Parsed Actions:
[
  {"sequence": 1, "action": "person walking on busy street"},
  {"sequence": 2, "action": "person checking phone"},
  {"sequence": 3, "action": "close-up phone screen with message"}
]
```

#### Step 3: Sequential Search
```python
def search_script_sequence(actions, results_per_action=3):
    """
    Search for each action in sequence
    """
    sequential_results = []
    
    for action in actions:
        # Enhance query
        variations = enhance_query(action['action'])
        
        # Search
        matches = search_with_variations(variations, top_k=results_per_action)
        
        sequential_results.append({
            'sequence': action['sequence'],
            'action': action,
            'matches': matches,
            'match_count': len(matches)
        })
    
    return sequential_results
```

**Output Format:**
```json
{
    "total_actions": 3,
    "results": [
        {
            "sequence": 1,
            "action": {"action": "person walking on busy street"},
            "matches": [
                {"clip_path": "scene_0042.mp4", "score": 0.89},
                {"clip_path": "scene_0103.mp4", "score": 0.85},
                {"clip_path": "scene_0217.mp4", "score": 0.82}
            ]
        },
        {
            "sequence": 2,
            "action": {"action": "person checking phone"},
            "matches": [
                {"clip_path": "scene_0078.mp4", "score": 0.91},
                {"clip_path": "scene_0156.mp4", "score": 0.87},
                {"clip_path": "scene_0234.mp4", "score": 0.84}
            ]
        },
        ...
    ]
}
```

---

## Complete Workflow Summary

### Input → Output Flow

```
RAW VIDEO (video.mp4)
    ↓
[YOLO Scene Detection]
    → Semantic signatures
    → Scene boundaries: [0s, 3.2s, 7.8s, 12.1s, ...]
    ↓
[FFmpeg Clip Extraction]
    → scene_0001.mp4 (0.0s - 3.2s)
    → scene_0002.mp4 (3.2s - 7.8s)
    → scene_0003.mp4 (7.8s - 12.1s)
    ↓
[Thumbnail Selection]
    → scene_0001.jpg (middle frame)
    → scene_0002.jpg (middle frame)
    → scene_0003.jpg (middle frame)
    ↓
[YOLO Object Analysis]
    → Objects: {person, cup, table}
    → Spatial: {person: center, cup: right}
    → Complexity: 3
    ↓
[Gemini Semantic Analysis]
    → Description: "Person at table with coffee..."
    → Scene Type: dialogue
    → Mood: calm, focused
    → Tags: [office, professional, coffee, ...]
    ↓
[Vector Embedding]
    → 384D vector: [0.23, -0.45, 0.67, ...]
    ↓
[ChromaDB Indexing]
    → Stored with metadata
    → Ready for search
    ↓
[SEARCH READY]
    → Query: "person drinking coffee" (any language)
    → Results: Ranked by semantic similarity
```

### Performance Metrics

| Stage | Time | Bottleneck | Optimization |
|-------|------|------------|--------------|
| YOLO Scene Detection | 1-2s/min | GPU | CUDA acceleration |
| Clip Extraction | 0.5s/clip | I/O | Hardware encoding |
| Thumbnail Selection | 0.1s/clip | I/O | Cached frames |
| YOLO Analysis | 0.2s/frame | GPU | Batch processing |
| Gemini Analysis | 1-2s/scene | API | Parallel requests |
| Vector Embedding | 0.1s/scene | CPU | Batch encoding |
| ChromaDB Indexing | 0.05s/scene | I/O | Batch inserts |
| **Total** | **~1-2s/scene** | **Gemini API** | **Parallelization** |

### Scalability

**Single Video (2 minutes):**
- ~10-15 scenes
- ~20-30 seconds total processing
- ~150 MB storage (clips + thumbnails + vectors)

**Large Library (100 videos, 200 minutes):**
- ~1000-1500 scenes
- ~30-50 minutes total processing (parallel)
- ~15 GB storage

**Search Performance:**
- Query time: <1 second
- Scales to millions of scenes
- HNSW algorithm: O(log n) complexity

---

## Why This Architecture Works

### 1. YOLO as the Foundation
- **Semantic understanding** from the start
- **Natural boundaries** based on content
- **Fast processing** with GPU acceleration
- **Consistent results** across different video types

### 2. Gemini as the Interpreter
- **Rich descriptions** beyond object detection
- **Context understanding** (mood, atmosphere, narrative)
- **Multilingual support** built-in
- **Flexible output** (JSON, structured data)

### 3. Vector Search as the Engine
- **Semantic matching** (not keyword matching)
- **Fast retrieval** (milliseconds)
- **Scalable** (millions of scenes)
- **Language-independent** (after translation)

### 4. Parallel Processing as the Accelerator
- **No artificial delays** (removed rate limiting)
- **Concurrent API calls** (5 scenes at once)
- **GPU utilization** (YOLO + encoding)
- **I/O optimization** (async file operations)

---

## Innovation Summary

**Traditional Video Search:**
- Manual tagging
- Keyword-based
- Time-consuming
- Language-specific

**TakeOne:**
- Automatic semantic analysis
- Concept-based search
- Real-time processing
- Multilingual native

**Key Differentiator:**
- **Script-to-Sequence Search** - No competitor offers this
- **YOLO-driven scene detection** - Semantic, not pixel-based
- **Gemini-powered understanding** - Human-level comprehension
- **End-to-end automation** - Upload → Search in minutes

---

**TakeOne: Where Computer Vision Meets Natural Language Understanding**

