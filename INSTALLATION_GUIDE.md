# CineSearch AI - Complete Installation Guide

## ⚠️ IMPORTANT: Installation Order Matters!

To ensure GPU acceleration works properly, you MUST install packages in this specific order:

---

## Prerequisites

### 1. FFmpeg (Required for Video Processing)

FFmpeg is required for video clipping and audio extraction.

**Quick Install (Run as Administrator):**
```powershell
powershell -ExecutionPolicy Bypass -File install_ffmpeg_auto.ps1
```

**Or use Package Manager:**
```cmd
# Using Chocolatey
choco install ffmpeg

# Using Scoop
scoop install ffmpeg
```

**Manual Installation:**
See `install_ffmpeg.bat` for detailed instructions.

**Verify Installation:**
```cmd
ffmpeg -version
```

---

## Step 1: Install PyTorch with CUDA Support

**Run this first:**
```cmd
install_pytorch_cuda.bat
```

This installs:
- PyTorch 2.x with CUDA 12.1
- TorchVision with CUDA support
- TorchAudio with CUDA support

**Why CUDA 12.1?** Your system has CUDA 12.7, which is backward compatible with CUDA 12.1 packages.

---

## Step 2: Install Core Dependencies

**Run this second:**
```cmd
pip install -r requirements.txt
```

This installs all packages EXCEPT torch-dependent ones:
- Streamlit (UI framework)
- Transformers (AI models)
- ChromaDB (vector database)
- OpenCV (video processing)
- Scene detection tools
- And more...

**Note:** `requirements.txt` has torch/torchvision/torchaudio commented out to prevent CUDA downgrade.

---

## Step 3: Install Torch-Dependent Packages

**Run this third:**
```cmd
pip install -r requirements-torch-dependent.txt
```

This installs packages that depend on PyTorch:
- **ultralytics** (YOLO object detection)
- **openai-whisper** (audio transcription)

These are installed separately because they might try to install CPU-only PyTorch if installed together.

---

## Alternative: One-Command Installation

**Or just run this:**
```cmd
install_requirements_safe.bat
```

This script does all 3 steps automatically in the correct order.

---

## Verification

After installation, verify GPU is detected:

```cmd
python check_gpu.py
```

Expected output:
```
✅ GPU READY - Your system will use GPU acceleration!
GPU Name: NVIDIA GeForce GTX 1650
CUDA Available: True
```

---

## Troubleshooting

### Problem: "No GPU detected - using CPU"

**Cause:** PyTorch was downgraded to CPU-only version

**Solution:**
1. Run `install_pytorch_cuda.bat` again
2. Check with: `python -c "import torch; print(torch.cuda.is_available())"`
3. Should print `True`

### Problem: "No module named 'ultralytics'" or "'whisper'"

**Cause:** Torch-dependent packages not installed

**Solution:**
```cmd
pip install -r requirements-torch-dependent.txt
```

### Problem: Streamlit won't start

**Cause:** Virtual environment broken or packages not installed

**Solution:**
```cmd
pip install streamlit
python -m streamlit run app.py
```

---

## Package List

### Core (requirements.txt)
- streamlit
- python-dotenv
- transformers
- openai
- chromadb
- google-generativeai
- sentence-transformers
- opencv-python
- moviepy
- Pillow
- scenedetect
- yt-dlp
- gdown
- requests
- numpy
- tqdm

### PyTorch (install separately)
- torch (CUDA 12.1)
- torchvision (CUDA 12.1)
- torchaudio (CUDA 12.1)

### Torch-Dependent (requirements-torch-dependent.txt)
- ultralytics (YOLO)
- openai-whisper (Audio)

---

## Why This Order?

1. **PyTorch CUDA first** - Ensures GPU support is installed
2. **Core packages second** - Won't interfere with PyTorch
3. **Torch-dependent last** - Uses existing CUDA PyTorch instead of installing CPU version

If you install in wrong order, pip might:
- Downgrade CUDA PyTorch to CPU-only version
- Install incompatible torch versions
- Break GPU acceleration

---

## Quick Start After Installation

```cmd
cd cinesearch-ai
streamlit run app.py
```

Or if that fails:
```cmd
python -m streamlit run app.py
```

The app will open at: http://localhost:8501
