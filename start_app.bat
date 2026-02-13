@echo off
echo ========================================
echo Kenya Smart Procurement AI - Quick Start
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.9+
    pause
    exit /b 1
)

echo [1/6] Checking Python version...
python --version

REM Check virtual environment
if not exist "venv\" (
    echo [2/6] Creating virtual environment...
    python -m venv venv
) else (
    echo [2/6] Virtual environment exists
)

REM Activate virtual environment
echo [3/6] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo [4/6] Installing dependencies...
pip install -r requirements.txt --quiet

REM Check .env file
if not exist ".env" (
    echo [5/6] Creating .env from template...
    copy .env.sample .env
    echo.
    echo [WARNING] Please edit .env and add your GOOGLE_API_KEY
    echo.
    pause
) else (
    echo [5/6] Environment file exists
)

REM Check Tesseract
tesseract --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Tesseract OCR not found
    echo Please install from: https://github.com/UB-Mannheim/tesseract/wiki
    echo.
)

echo [6/6] Starting application...
echo.
echo ========================================
echo Application starting at http://localhost:8501
echo Press Ctrl+C to stop
echo ========================================
echo.

streamlit run ui/app.py

pause
