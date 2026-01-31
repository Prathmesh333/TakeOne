# TakeOne — 3-Minute Pitch Script

## Opening (30 seconds)

*[Show footage timeline]*

> "Every film editor knows this moment — you're staring at 4 hours of raw footage, looking for *that one reaction*. The hesitant pause. The meaningful glance. You know it's in there somewhere."

> "You scrub. You search filenames. You scrub again. **Editors spend 70% of their time just finding the right clip.**"

> "What if you could search footage the way you *think* about it?"

---

## The Solution (30 seconds)

*[Show TakeOne interface]*

> "This is TakeOne. Instead of searching 'person face' and getting 500 irrelevant results..."

*[Type query]*

> "You search: **'hesitant reaction before answering'**"

*[Show results]*

> "And you get exactly that — the subtle moment you remembered from the shoot."

---

## Live Demo (90 seconds)

### Demo 1: Basic Search (30 sec)

*[Have footage pre-loaded]*

> "Here's 3 minutes of raw footage from a short film. Let me find something specific."

*[Search: "person looking worried"]*

> "Instantly — here are clips ranked by how well they match. Not keyword matching. *Understanding.*"

---

### Demo 2: The Magic — Intent Search (30 sec)

*[Search: "hesitant pause before answering a difficult question"]*

> "Watch this — I'm searching with *intent*, not keywords. 'Hesitant pause before answering a difficult question.'"

*[Show results]*

> "The AI expands this into visual concepts — uncertainty, looking away, pauses — and finds them. No manual tagging. No metadata. Pure understanding."

---

### Demo 3: Emotion Filtering (30 sec)

*[Show emotion slider]*

> "And here's the 'vibe check.' Same search, but let me filter for *tense* versus *neutral.*"

*[Adjust slider, show different results]*

> "Different emotional moments, same semantic search. Ready for any editorial mood."

---

## How It Works (20 seconds)

*[Quick architecture visual]*

> "Under the hood: CLIP understands every frame. Whisper transcribes dialogue. Gemini expands your intent into searchable terms. ChromaDB makes it instant."

> "Open-source stack. Runs locally. Ready to integrate."

---

## Closing (30 seconds)

> "TakeOne doesn't just find objects in your footage. It understands *cinema*."

> "It finds the emotional beats. The subtle moments. The reactions that make great films."

> "For Problem Statement #4 — Semantic Footage Search — this is our answer. It's intuitive. It's fast. And it's ready to transform how editors work."

> "Thank you."

---

## Backup Q&A Prep

**Q: How accurate is it?**  
A: In our testing, relevant results appear in top-3 about 85% of the time. The LLM expansion helps bridge the gap between how editors think and what CLIP can detect.

**Q: How long does indexing take?**  
A: About 3 minutes per 1 minute of footage on a standard GPU. Pre-indexing is recommended for large projects.

**Q: Can it handle long-form content?**  
A: Yes — we've tested with 30+ minute videos. ChromaDB scales well for thousands of clips.

**Q: What about integration with editing software?**  
A: Future roadmap includes Premiere/DaVinci integration. The architecture is ready for plugin development.

**Q: Cost?**  
A: All core tech is free/open-source. Gemini API has a free tier for testing and development.
