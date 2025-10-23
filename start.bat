# Wi-Fi Signal Analyzer - Quick Start Script (Windows CMD/PowerShell compatible)
@echo off
echo ========================================
echo   Wi-Fi Signal Strength Analyzer
echo ========================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found! Please install Python 3.8+
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python found
echo.

echo Installing dependencies...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [WARNING] Some dependencies may have issues
) else (
    echo [OK] Dependencies installed
)

echo.
echo ========================================
echo Starting Server...
echo ========================================
echo.
echo Dashboard: http://localhost:5000
echo.
echo Press Ctrl+C to stop
echo.

python app.py
