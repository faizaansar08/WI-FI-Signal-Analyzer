@echo off
title WiFi Analyzer Server - KEEP THIS WINDOW OPEN
color 0A
cls

echo.
echo ============================================================
echo          Wi-Fi Signal Strength Analyzer Server
echo ============================================================
echo.
echo  Starting server on: http://localhost:5000
echo.
echo  IMPORTANT: KEEP THIS WINDOW OPEN!
echo  Close this window to stop the server.
echo.
echo ============================================================
echo.

cd /d "d:\cn project"
python app.py

echo.
echo ============================================================
echo Server stopped. Press any key to exit...
pause > nul
