# Script Search Test Examples

This guide provides sample videos and scripts to test the Script-to-Sequence Search feature.

---

## 🎬 Test Scenario 1: Action Sequence

### Video Source
**Free Stock Footage:**
- **Pexels**: https://www.pexels.com/search/videos/action%20sequence/
- **Pixabay**: https://pixabay.com/videos/search/action/
- **Videvo**: https://www.videvo.net/free-video/action/

**Recommended Video:**
Search for "person running chase scene" or "action sequence" on Pexels

### Test Script (English)

```
A person runs down a busy city street looking panicked.
They glance over their shoulder checking if someone is following.
The person ducks into an alley to hide.
They pull out their phone with shaking hands.
A close-up shows them typing an urgent message.
```

### Test Script (Hindi)

```
एक व्यक्ति घबराया हुआ व्यस्त शहर की सड़क पर दौड़ रहा है।
वे अपने कंधे के ऊपर देखते हैं कि कोई पीछा तो नहीं कर रहा।
व्यक्ति छिपने के लिए एक गली में घुस जाता है।
वे कांपते हाथों से अपना फोन निकालते हैं।
एक क्लोज-अप में वे एक जरूरी संदेश टाइप करते दिखाई देते हैं।
```

### Expected Results
- **5 sequential actions**
- Each action should return 3 footage options
- Results should be in order (Action 1 → 2 → 3 → 4 → 5)

---

## 🎬 Test Scenario 2: Dialogue Scene

### Video Source
**YouTube (Creative Commons):**
- Search: "conversation scene creative commons"
- Search: "interview footage free"
- Search: "dialogue scene stock footage"

**Direct Links (Free):**
- Pexels: https://www.pexels.com/search/videos/conversation/
- Mixkit: https://mixkit.co/free-stock-video/conversation/

### Test Script (English)

```
Two people sit across from each other at a coffee shop.
One person speaks with animated hand gestures.
The other person listens intently, nodding occasionally.
A waiter brings coffee to the table.
Both people smile and continue their conversation.
```

### Test Script (Tamil)

```
இரண்டு நபர்கள் ஒரு காபி கடையில் ஒருவருக்கொருவர் எதிரே அமர்ந்திருக்கிறார்கள்.
ஒரு நபர் கை சைகைகளுடன் பேசுகிறார்.
மற்றவர் கவனமாக கேட்டு, எப்போதாவது தலையசைக்கிறார்.
ஒரு பணியாளர் மேசைக்கு காபி கொண்டு வருகிறார்.
இருவரும் சிரித்துக்கொண்டே தங்கள் உரையாடலைத் தொடர்கிறார்கள்.
```

### Expected Results
- **5 sequential actions**
- Should find conversation/dialogue scenes
- Results organized by sequence

---

## 🎬 Test Scenario 3: Emotional Journey

### Video Source
**Free Emotional Footage:**
- Pexels: https://www.pexels.com/search/videos/emotion/
- Videvo: https://www.videvo.net/free-video/emotion/

### Test Script (English)

```
A person sits alone looking sad and thoughtful.
They receive a phone call and their expression changes.
A smile slowly appears on their face.
They stand up with renewed energy.
The person walks confidently toward the camera.
```

### Test Script (Spanish)

```
Una persona se sienta sola luciendo triste y pensativa.
Reciben una llamada telefónica y su expresión cambia.
Una sonrisa aparece lentamente en su rostro.
Se levantan con energía renovada.
La persona camina con confianza hacia la cámara.
```

### Expected Results
- **5 sequential actions**
- Should capture emotional progression
- Mood changes reflected in results

---

## 🎬 Test Scenario 4: Simple Daily Activity

### Video Source
**Easy to Find:**
- Pexels: https://www.pexels.com/search/videos/morning%20routine/
- Pixabay: https://pixabay.com/videos/search/daily%20life/

### Test Script (English)

```
A person wakes up and stretches in bed.
They walk to the kitchen.
They pour a cup of coffee.
They sit down and look at their phone.
```

### Test Script (French)

```
Une personne se réveille et s'étire dans son lit.
Elle marche vers la cuisine.
Elle verse une tasse de café.
Elle s'assoit et regarde son téléphone.
```

### Expected Results
- **4 sequential actions**
- Simple, common scenes
- Should be easy to find matches

---

## 🎬 Test Scenario 5: Nature/Outdoor Scene

### Video Source
**Nature Footage (Abundant):**
- Pexels: https://www.pexels.com/search/videos/nature/
- Pixabay: https://pixabay.com/videos/search/landscape/

### Test Script (English)

```
The sun rises over a mountain range.
Birds fly across the sky.
A river flows through a valley.
Trees sway gently in the wind.
The camera pans across a beautiful landscape.
```

### Test Script (German)

```
Die Sonne geht über einer Bergkette auf.
Vögel fliegen über den Himmel.
Ein Fluss fließt durch ein Tal.
Bäume wiegen sich sanft im Wind.
Die Kamera schwenkt über eine wunderschöne Landschaft.
```

### Expected Results
- **5 sequential actions**
- Nature/landscape footage
- Cinematic shots

---

## 📝 How to Test

### Step 1: Get Test Video

**Option A: Download from Pexels**
1. Go to https://www.pexels.com/videos/
2. Search for relevant footage
3. Download MP4 file
4. Save to your computer

**Option B: Use YouTube URL**
1. Find Creative Commons video on YouTube
2. Copy the URL
3. Use TakeOne's URL upload feature

### Step 2: Index the Video

1. Open TakeOne app (`streamlit run app.py`)
2. Go to **Library** tab
3. Click **Upload Video** or **Process from URL**
4. Select/paste your video
5. Wait for processing (shows progress)
6. Video is now indexed and searchable

### Step 3: Test Script Search

1. Go to **Home** tab
2. Select **Script Sequence Search** mode
3. Paste one of the test scripts above
4. Click **Search Script**
5. Review sequential results

### Step 4: Verify Results

**Check for:**
- ✅ Correct number of actions parsed
- ✅ Results in sequential order (1 → 2 → 3...)
- ✅ Multiple footage options per action
- ✅ Relevant matches for each action
- ✅ Video players work
- ✅ Metadata displayed (timestamps, mood, tags)

### Step 5: Test Export

1. Click **Copy Edit List** - Should show formatted text
2. Click **Download CSV** - Should download CSV file
3. Verify export contains all actions and matches

---

## 🌍 Multilingual Testing

### Test Translation Feature

**Try the same script in different languages:**

1. **English** → Should work directly
2. **Hindi** → Should translate and search
3. **Tamil** → Should translate and search
4. **Spanish** → Should translate and search
5. **French** → Should translate and search

**Verify:**
- Translation happens automatically
- Results are the same regardless of language
- No errors in console

---

## 🎯 Quick Test Script (Universal)

**Use this simple script for quick testing:**

```
A person walks down a street.
They stop and look around.
They pull out their phone.
They start walking again.
```

**Why this works:**
- Very common footage types
- Easy to find in any stock library
- Simple actions
- Works in any language

---

## 📊 Expected Performance

| Metric | Expected Value |
|--------|---------------|
| Script parsing | 1-2 seconds |
| Translation (if needed) | 0.5-1 second |
| Search per action | 1-2 seconds |
| Total for 5 actions | 5-10 seconds |
| Results per action | 3 options (configurable) |

---

## 🐛 Troubleshooting

### No Results Found

**Possible causes:**
1. Video not indexed yet
2. Script actions too specific
3. Database empty

**Solutions:**
- Index more videos
- Use simpler, more general actions
- Check database has content

### Wrong Sequence Order

**Possible causes:**
1. Script not parsed correctly
2. Actions too similar

**Solutions:**
- Make actions more distinct
- Use clear sequential language
- Check parsed actions in results

### Translation Not Working

**Possible causes:**
1. GEMINI_API_KEY not set
2. API quota exceeded

**Solutions:**
- Check .env file
- Verify API key is valid
- Check Google Cloud console for quota

---

## 💡 Tips for Best Results

### Writing Good Scripts

**DO:**
- ✅ Use clear, visual descriptions
- ✅ One action per line
- ✅ Focus on what's visible
- ✅ Use simple language
- ✅ Keep actions distinct

**DON'T:**
- ❌ Use abstract concepts
- ❌ Include dialogue text
- ❌ Make actions too similar
- ❌ Use overly complex descriptions
- ❌ Mix multiple actions in one line

### Example: Good vs Bad

**❌ Bad Script:**
```
The protagonist contemplates their existential crisis.
They experience a moment of profound realization.
```

**✅ Good Script:**
```
A person sits alone looking thoughtful.
They suddenly look up with a surprised expression.
```

---

## 🎬 Sample Videos to Download

### Recommended Free Sources

1. **Pexels Videos** (Best quality, no attribution required)
   - https://www.pexels.com/videos/

2. **Pixabay Videos** (Good variety)
   - https://pixabay.com/videos/

3. **Mixkit** (Curated collections)
   - https://mixkit.co/free-stock-video/

4. **Videvo** (Large library)
   - https://www.videvo.net/

5. **Coverr** (Beautiful footage)
   - https://coverr.co/

### Suggested Search Terms

- "person walking"
- "conversation"
- "city street"
- "office work"
- "coffee shop"
- "phone call"
- "running"
- "sunset"
- "nature"
- "daily routine"

---

## 📋 Test Checklist

- [ ] Downloaded test video
- [ ] Indexed video in TakeOne
- [ ] Tested English script
- [ ] Tested non-English script (Hindi/Tamil/Spanish)
- [ ] Verified sequential results
- [ ] Checked all actions parsed correctly
- [ ] Tested export to CSV
- [ ] Tested copy edit list
- [ ] Verified video playback
- [ ] Checked metadata display
- [ ] Tested with different result counts (1-5 per action)

---

**Ready to test!** 🚀

Start with Scenario 4 (Simple Daily Activity) - it's the easiest to find footage for and test.
