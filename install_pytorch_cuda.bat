@echo off
echo ========================================
echo Installing PyTorch with CUDA Support
echo ========================================
echo.
echo Your GPU: NVIDIA GeForce GTX 1650
echo CUDA Version: 12.7
echo.
echo This will uninstall CPU-only PyTorch and install CUDA-enabled version
echo.
pause

echo.
echo Step 1: Uninstalling CPU-only PyTorch...
pip uninstall -y torch torchvision torchaudio

echo.
echo Step 2: Installing PyTorch with CUDA 12.1 support...
echo (CUDA 12.1 is compatible with your CUDA 12.7 driver)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

echo.
echo Step 3: Verifying installation...
python -c "import torch; print('PyTorch version:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('CUDA version:', torch.version.cuda); print('GPU Name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"

echo.
echo ========================================
echo Installation Complete!
echo ========================================
pause
