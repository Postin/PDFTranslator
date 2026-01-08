@echo off
REM Simple launcher for PDF Translator Web UI (Windows)

echo PDF Translator
echo =================

REM Check for .env
if not exist .env (
    echo Error: .env file not found
    echo Create .env with your OpenAI API key:
    echo   echo OPENAI_API_KEY=your-key-here ^> .env
    pause
    exit /b 1
)

REM Activate virtual environment if exists
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

echo Starting web interface...
echo Open http://localhost:8501 in your browser
echo.

streamlit run app.py

