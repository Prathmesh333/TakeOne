# Quick Start Guide

## 1. Start the App
```bash
cd cinesearch-ai
streamlit run app.py
```

## 2. Initialize Engine
1. Click **⚙️ Settings** in sidebar
2. Click **"Initialize / Reload Engine"**
3. Wait for "Engine Online" message

## 3. Process a Video

### From File:
1. Go to **📁 Library** tab
2. Upload video file
3. Click **"Process X Videos"**
4. Watch progress bars update

### From URL:
1. Go to **📁 Library** tab
2. Click **"From URL"** tab
3. Paste YouTube URL
4. Click **"Process from URL"**

## 4. Search
1. Go to **🏠 Home** tab
2. Enter search query (e.g., "person walking")
3. Click **"Search"**
4. View results with thumbnails
5. Click **"Show Full Analysis"** for details

---

## What You'll See

### Progress Bars (Real-time)
```
Overall: File 1/1 ████████████████ 100%
Stage: Gemini Analysis: 3/5 (60%) ████████░░░░░░░░
Status: 📹 video.mp4 - Gemini Analysis: 3/5
```

### Processing Stages
1. **Scene Detection** - YOLO finds scene boundaries (5-10s)
2. **Clip Extraction** - FFmpeg cuts clips (3-5s)
3. **Thumbnails** - Best frame extraction (2-3s)
4. **YOLO Analysis** - Quick object detection (1-2s)
5. **Gemini Analysis** - Detailed AI analysis (15-30s)
6. **Indexing** - Store in ChromaDB (1-2s)

### Search Results
- Video player with clip
- Match percentage (e.g., 95%)
- Scene type, mood badges
- Description and tags
- **"Show Full Analysis"** button for complete metadata

---

## Common Issues

### ❌ API Key Missing
**Fix**: Add to `.env` file:
```
GEMINI_API_KEY=your_key_here
```

### ❌ FFmpeg Not Found
**Fix**: Run `install_ffmpeg_auto.ps1`

### ⚠️ No GPU Detected
**Impact**: Slower processing (still works)
**Fix**: Install CUDA toolkit (optional)

### ❌ YouTube 403 Error
**Fix**: Wait a few minutes, try different video

---

## Tips

- ✅ Use GPU for 2-3x faster processing
- ✅ Process 2-5 minute videos for best results
- ✅ Use specific search terms ("person walking" vs "person")
- ✅ Click "Show Full Analysis" to see all metadata
- ✅ Check console logs if something seems stuck

---

## Expected Performance

**2-minute video**: ~30-50 seconds
**10-minute video**: ~2-3 minutes

With GPU: 2-3x faster
Without GPU: Still works, just slower

---

## Need Help?

Check these files:
- `WHAT_TO_EXPECT.md` - Detailed guide
- `FIXES_SUMMARY.md` - Recent fixes
- `LATEST_FIXES.md` - Technical details
- `OPTIMIZED_FLOW.md` - How it works

---

**That's it! You're ready to search your videos semantically.** 🎬✨
