# Script-to-Sequence Search - Testing Guide

## Quick Test Instructions

### 1. Start the Application
```bash
cd cinesearch-ai
python -m streamlit run app.py
```

### 2. Initialize the Engine
- Go to Home page
- Click "Initialize / Reload Engine" button
- Wait for initialization to complete

### 3. Test Script Search

#### Navigate to Script Search Mode
1. On the Home page, look for "Search Mode" section
2. Select **"Script Sequence Search"** radio button
3. You'll see a blue info box explaining the feature

#### Test Script 1 (Simple - 3 Actions)
Paste this into the script text area:
```
A person walks down a busy city street, looking worried.
They stop and check their phone with a concerned expression.
The person starts running through the crowd.
```

- Set "Results per action" to 3
- Click "Search Script" button
- **Expected**: 3 actions parsed, results shown in sequence with numbered circles

#### Test Script 2 (Medium - 5 Actions)
```
A detective walks into a dimly lit office.
He sits down at his desk, looking exhausted.
Close-up of his hands opening a case file.
His expression changes to shock as he reads.
He quickly grabs his phone and makes a call.
```

- Set "Results per action" to 2
- Click "Search Script"
- **Expected**: 5 actions, each with 2 footage options

#### Test Script 3 (Complex - 7 Actions)
```
INT. COFFEE SHOP - DAY
Sarah enters, looking around nervously.
She spots John at a corner table.
Close-up: Sarah's worried expression.
She walks over to John's table.
They exchange tense glances.
John slides an envelope across the table.
Sarah opens it and her face goes pale.
```

- Set "Results per action" to 3
- Click "Search Script"
- **Expected**: 7 actions parsed, sequential display

### 4. Test Export Features

After getting results:

#### Test "Copy Edit List"
1. Click "📋 Copy Edit List" button
2. **Expected**: Text format edit list appears in code block
3. Verify it shows:
   - All actions in sequence
   - Multiple options per action
   - File paths, scores, durations

#### Test "Download CSV"
1. Click "💾 Download CSV" button
2. Click "Download" in the popup
3. **Expected**: `edit_sequence.csv` file downloads
4. Open in Excel/Sheets
5. Verify columns: Sequence, Action, Clip Path, Score, Duration, Description

### 5. Verify Results Display

For each action, check:
- ✅ Sequence number in cyan circle (1, 2, 3, ...)
- ✅ Action description
- ✅ Number of options badge
- ✅ Thumbnail images for each option
- ✅ Video players working
- ✅ Match scores displayed (e.g., "95% Match")
- ✅ Duration shown

### 6. Test Edge Cases

#### Empty Script
- Leave script area empty
- Click "Search Script"
- **Expected**: No action (button should be disabled or show warning)

#### Single Line Script
```
A person walking in the park.
```
- **Expected**: 1 action, results shown

#### Very Long Script (10+ actions)
```
Person wakes up in bed.
Gets out of bed and stretches.
Walks to bathroom.
Brushes teeth.
Takes a shower.
Gets dressed.
Makes coffee in kitchen.
Reads newspaper.
Grabs car keys.
Walks out the door.
Gets in car and drives away.
```
- **Expected**: All actions parsed and searched sequentially
- May take 20-30 seconds (normal)

### 7. Compare with Quick Search

Switch back to "Quick Search" mode:
- Verify normal search still works
- Search for: "person walking"
- **Expected**: Regular grid results (not sequential)

Switch back to "Script Sequence Search":
- Verify mode switching works smoothly

## What to Look For

### ✅ Success Indicators
- Script parses into numbered actions
- Results appear in sequence order
- Each action has multiple footage options
- Thumbnails and videos load correctly
- Export buttons work
- CSV downloads successfully
- Edit list is readable and complete

### ❌ Potential Issues

**Issue**: "GEMINI_API_KEY not set"
- **Fix**: Add API key to `.env` file

**Issue**: Script parsing fails
- **Check**: Gemini API quota/limits
- **Fallback**: Should use line-by-line parsing automatically

**Issue**: No results for some actions
- **Normal**: Some actions may not have matches in database
- **Shows**: "No matches found for action X"

**Issue**: Slow performance
- **Normal**: 1-2 seconds per action with query expansion
- **Expected**: 5 actions = ~10 seconds total

**Issue**: Export buttons don't work
- **Check**: Browser console for errors
- **Try**: Refresh page and search again

## Performance Benchmarks

| Script Size | Expected Time | Notes |
|-------------|---------------|-------|
| 1-3 actions | 5-10 seconds | Fast |
| 4-7 actions | 10-20 seconds | Normal |
| 8-12 actions | 20-40 seconds | Acceptable |
| 13+ actions | 40+ seconds | Consider splitting |

## Demo Script for Presentation

Use this for impressive demo:
```
INT. DETECTIVE'S OFFICE - NIGHT
A weary detective enters his dimly lit office.
He collapses into his chair, exhausted from the case.
Close-up: His hands trembling as he opens a case file.
His eyes widen in shock at what he reads.
He frantically searches through papers on his desk.
Finding a photo, he holds it up to the light.
His expression changes from shock to determination.
He grabs his coat and rushes out the door.
```

**Why this works**:
- 8 clear, visual actions
- Variety of shot types (wide, close-up, medium)
- Emotional progression
- Cinematic narrative
- Easy to find matching footage

## Troubleshooting

### Script Not Parsing
1. Check Gemini API key is valid
2. Check internet connection
3. Try simpler script (3-4 lines)
4. Check browser console for errors

### No Results Showing
1. Verify database has indexed content
2. Check "Statistics" in sidebar shows scenes
3. Try Quick Search first to verify system works
4. Simplify script actions

### Export Not Working
1. Check browser allows downloads
2. Try different browser
3. Check file permissions
4. Try "Copy Edit List" instead of CSV

## Success Criteria

✅ Script parses into actions  
✅ Results display in sequence  
✅ Multiple options per action  
✅ Videos play correctly  
✅ Export functions work  
✅ CSV imports into editing software  
✅ Performance is acceptable  
✅ UI is intuitive and clear  

## Next Steps After Testing

If all tests pass:
1. Commit changes
2. Push to GitHub
3. Update README with new feature
4. Prepare demo for jury/mentors
5. Consider adding to pitch deck

## Questions to Answer During Testing

- [ ] Is the script parsing accurate?
- [ ] Are results truly in sequence order?
- [ ] Is the UI intuitive for producers/editors?
- [ ] Do export formats work with editing software?
- [ ] Is performance acceptable for production use?
- [ ] Are error messages clear and helpful?
- [ ] Does it handle edge cases gracefully?

---

**Ready to revolutionize film production workflow!** 🎬
