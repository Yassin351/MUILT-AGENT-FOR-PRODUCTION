@echo off
echo ========================================
echo Running Test Suite
echo ========================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

echo [1/3] Running tests...
pytest -v

echo.
echo [2/3] Generating coverage report...
pytest --cov=. --cov-report=html --cov-report=term-missing

echo.
echo [3/3] Opening coverage report...
start htmlcov\index.html

echo.
echo ========================================
echo Test suite complete!
echo Coverage report opened in browser
echo ========================================
pause
