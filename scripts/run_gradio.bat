@echo off
echo Starting CineSearch AI (Gradio Interface)...
echo.

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Run Gradio app
python app_gradio.py

pause
