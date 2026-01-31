# How to Fix Video Display Issue

## What's the Problem?

If you're seeing:
- ❌ Black video player in search results
- ❌ No thumbnail images showing
- ❌ Videos not playing

This is because your database has incorrect file paths.

## Quick Fix (5 minutes)

### Step 1: Open Terminal
Navigate to your project folder:
```bash
cd cinesearch-ai
```

### Step 2: Run the Fix Script
```bash
python clear_and_reindex.py
```

### Step 3: Follow the Prompts
The script will:
1. Show you current database stats
2. Ask for confirmation (type `yes`)
3. Archive your old database (backup)
4. Re-analyze all your videos
5. Create a new database with correct paths

### Step 4: Test in Streamlit
```bash
python -m streamlit run app.py
```

Search for something and verify:
- ✅ Thumbnails appear
- ✅ Videos play correctly

## What Does the Script Do?

1. **Backs up** your current database to `chroma_db_archives/`
2. **Finds** all existing video clips in `output/clips/`
3. **Re-analyzes** them with Gemini (uses existing thumbnails)
4. **Re-indexes** with correct video paths

## How Long Does It Take?

- **Small library** (1-2 videos): ~2-3 minutes
- **Medium library** (5-10 videos): ~5-10 minutes
- **Large library** (20+ videos): ~15-30 minutes

Time depends on:
- Number of clips
- Gemini API speed
- Your internet connection

## Alternative: Start Fresh

If you want to start over:

1. Open Streamlit UI
2. Go to "Library Management"
3. Click "Create New Library"
4. Give it a name
5. Process your videos again

Your old library will be archived automatically.

## Troubleshooting

### "GEMINI_API_KEY not set"
Add your API key to `.env` file:
```
GEMINI_API_KEY=your_key_here
```

### "No clips directory found"
You need to process at least one video first through the Streamlit UI.

### Script fails or crashes
1. Check your internet connection
2. Verify Gemini API key is valid
3. Try processing one video at a time through the UI

## Need Help?

Check these files:
- `FIX_SUMMARY.md` - Quick overview
- `kiro_docs/56_VIDEO_DISPLAY_FIX.md` - Technical details
- `QUICK_START.md` - General usage guide

## What Changed?

The pipeline now:
- ✅ Uses thumbnails for Gemini analysis (faster, cheaper)
- ✅ Stores video paths in database (for playback)
- ✅ Keeps both paths separate and correct

All new videos processed after this fix will work automatically!

---

**Status**: ✅ Fixed in code  
**Action**: Run `python clear_and_reindex.py`  
**Time**: ~5-30 minutes depending on library size
