@echo off
echo ============================================================
echo FFmpeg Installation Guide for Windows
echo ============================================================
echo.
echo FFmpeg is required for video processing (clipping, audio extraction).
echo.
echo OPTION 1: Install via Chocolatey (Recommended - Easiest)
echo --------------------------------------------------------
echo If you have Chocolatey installed, run:
echo   choco install ffmpeg
echo.
echo To install Chocolatey first, visit: https://chocolatey.org/install
echo.
echo.
echo OPTION 2: Install via Scoop (Alternative Package Manager)
echo --------------------------------------------------------
echo If you have Scoop installed, run:
echo   scoop install ffmpeg
echo.
echo To install Scoop first, run in PowerShell:
echo   Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
echo   irm get.scoop.sh ^| iex
echo.
echo.
echo OPTION 3: Manual Installation
echo --------------------------------------------------------
echo 1. Download FFmpeg from: https://www.gyan.dev/ffmpeg/builds/
echo    - Click "ffmpeg-release-essentials.zip"
echo.
echo 2. Extract the ZIP file to: C:\ffmpeg
echo.
echo 3. Add to PATH:
echo    - Open "Environment Variables" (search in Start menu)
echo    - Under "System variables", find "Path" and click "Edit"
echo    - Click "New" and add: C:\ffmpeg\bin
echo    - Click "OK" on all dialogs
echo.
echo 4. Restart your terminal/command prompt
echo.
echo 5. Verify installation:
echo    ffmpeg -version
echo.
echo ============================================================
echo After installation, restart your terminal and run the app again
echo ============================================================
pause
