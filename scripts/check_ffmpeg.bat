@echo off
echo Checking for FFmpeg...
echo.

ffmpeg -version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ FFmpeg is installed!
    echo.
    ffmpeg -version | findstr "ffmpeg version"
    echo.
    echo You're ready to process videos!
) else (
    echo ❌ FFmpeg is NOT installed
    echo.
    echo FFmpeg is required for video processing.
    echo.
    echo To install, choose one option:
    echo.
    echo 1. Auto-install (Recommended):
    echo    powershell -ExecutionPolicy Bypass -File install_ffmpeg_auto.ps1
    echo.
    echo 2. Manual install:
    echo    Run: install_ffmpeg.bat
    echo.
    echo 3. Package manager:
    echo    choco install ffmpeg
    echo    OR
    echo    scoop install ffmpeg
)

echo.
pause
