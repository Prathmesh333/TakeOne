# Installation & Setup Scripts

This folder contains installation and setup scripts for TakeOne.

## Installation Scripts

### FFmpeg Installation
- **`install_ffmpeg_auto.ps1`** - Automatic FFmpeg installation (PowerShell)
  ```powershell
  .\scripts\install_ffmpeg_auto.ps1
  ```
  Downloads and installs FFmpeg automatically

- **`install_ffmpeg.bat`** - Manual FFmpeg installation guide (Batch)
  ```cmd
  scripts\install_ffmpeg.bat
  ```

- **`check_ffmpeg.bat`** - Check if FFmpeg is installed and working
  ```cmd
  scripts\check_ffmpeg.bat
  ```

### PyTorch & CUDA Installation
- **`install_pytorch_cuda.bat`** - Install PyTorch with CUDA support
  ```cmd
  scripts\install_pytorch_cuda.bat
  ```
  Installs PyTorch with CUDA 12.1 for GPU acceleration

### Dependencies Installation
- **`install_requirements_safe.bat`** - Safe installation of Python dependencies
  ```cmd
  scripts\install_requirements_safe.bat
  ```
  Installs requirements with error handling

## Running Scripts

### Gradio UI
- **`run_gradio.bat`** - Launch Gradio interface (alternative UI)
  ```cmd
  scripts\run_gradio.bat
  ```

## Setup Order

For first-time setup, run in this order:

### 1. Install FFmpeg
```powershell
# Windows PowerShell (Recommended)
.\scripts\install_ffmpeg_auto.ps1

# Or check manually
scripts\check_ffmpeg.bat
```

### 2. Install PyTorch with CUDA
```cmd
scripts\install_pytorch_cuda.bat
```

### 3. Install Dependencies
```cmd
scripts\install_requirements_safe.bat
```

### 4. Verify Installation
```bash
# Check GPU
python tests/check_gpu.py

# Check FFmpeg
scripts\check_ffmpeg.bat

# Check Gemini API
python tests/diagnose_gemini.py
```

## Platform-Specific Notes

### Windows
- Use PowerShell for `.ps1` scripts
- Use Command Prompt for `.bat` scripts
- May need to enable script execution:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

### Linux/Mac
- FFmpeg: `sudo apt install ffmpeg` (Ubuntu) or `brew install ffmpeg` (Mac)
- PyTorch: Use pip command from [pytorch.org](https://pytorch.org)
- Scripts: Convert `.bat` to `.sh` or run commands manually

## Troubleshooting

### FFmpeg Not Found
```cmd
scripts\check_ffmpeg.bat
```
If not found, run `install_ffmpeg_auto.ps1`

### CUDA Not Available
```cmd
scripts\install_pytorch_cuda.bat
```
Reinstall PyTorch with CUDA support

### Permission Denied (PowerShell)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Manual Installation

If scripts fail, install manually:

### FFmpeg
1. Download from: https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add to PATH: `C:\ffmpeg\bin`

### PyTorch with CUDA
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Dependencies
```bash
pip install -r requirements.txt
```

---

**Note:** These scripts are for initial setup. Once installed, use `streamlit run app.py` to launch TakeOne.
