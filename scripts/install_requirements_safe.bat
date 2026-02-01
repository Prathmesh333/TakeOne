@echo off
echo ============================================================
echo CineSearch AI - Complete Installation Script
echo Preserves CUDA PyTorch and installs all dependencies
echo ============================================================
echo.

echo Step 1: Installing PyTorch with CUDA 12.1 support...
echo This may take several minutes...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
if %errorlevel% neq 0 (
    echo ERROR: PyTorch CUDA installation failed!
    pause
    exit /b 1
)
echo.

echo Step 2: Verifying PyTorch CUDA installation...
python -c "import torch; print('PyTorch:', torch.__version__); print('CUDA available:', torch.cuda.is_available())"
if %errorlevel% neq 0 (
    echo ERROR: PyTorch verification failed!
    pause
    exit /b 1
)
echo.

echo Step 3: Installing core requirements (torch excluded)...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Requirements installation failed!
    pause
    exit /b 1
)
echo.

echo Step 4: Installing torch-dependent packages...
echo Installing ultralytics (YOLO)...
pip install ultralytics>=8.0.0 --no-deps
pip install ultralytics>=8.0.0
echo.

echo Installing openai-whisper (Audio transcription)...
pip install openai-whisper>=20231117 --no-deps
pip install openai-whisper>=20231117
echo.

echo Step 5: Final verification...
python -c "import torch; print('PyTorch:', torch.__version__); print('CUDA:', torch.cuda.is_available())"
echo.

echo Step 6: Testing GPU detection...
python check_gpu.py
echo.

echo ============================================================
echo Installation complete!
echo You can now run: streamlit run app.py
echo ============================================================
pause
