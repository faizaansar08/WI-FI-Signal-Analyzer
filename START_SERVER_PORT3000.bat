@echo off
title WiFi Analyzer Server - PORT 3000
color 0A
cls

echo.
echo ============================================================
echo          Wi-Fi Signal Strength Analyzer
echo ============================================================
echo.
echo  Starting server on: http://localhost:3000
echo.
echo  KEEP THIS WINDOW OPEN!
echo.
echo ============================================================
echo.

cd /d "d:\cn project"

python app_simple.py

echo.
echo.
echo ============================================================
echo SERVER CRASHED OR STOPPED!
echo.
echo Check the error message above.
echo.
pause
