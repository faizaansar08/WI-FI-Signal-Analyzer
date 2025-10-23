@echo off
title WiFi Analyzer - WORKING VERSION (Port 8080)
color 0B
cls

echo.
echo ============================================================
echo     Wi-Fi Signal Strength Analyzer - COMPLETE VERSION
echo ============================================================
echo.
echo  Server will start on: http://localhost:8080
echo.
echo  IMPORTANT: KEEP THIS WINDOW OPEN!
echo.
echo  Features:
echo    - Real-time WiFi Scanning
echo    - Live Signal Monitoring
echo    - Interactive Graphs
echo    - ML Predictions (if model available)
echo.
echo ============================================================
echo.

cd /d "d:\cn project"

echo Starting server...
echo.

python app_working.py

echo.
echo ============================================================
echo Server stopped.
pause
