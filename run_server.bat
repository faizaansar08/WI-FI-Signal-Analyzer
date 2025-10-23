@echo off
cd /d "d:\cn project"
echo ============================================================
echo Starting Wi-Fi Signal Strength Analyzer Server
echo ============================================================
echo.
echo Server will start on: http://localhost:5000
echo.
echo KEEP THIS WINDOW OPEN while using the application!
echo Press Ctrl+C to stop the server
echo.
echo ============================================================
echo.
python app.py
pause
