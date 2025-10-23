@echo off
echo.
echo ========================================
echo   Multi-Network WiFi Analyzer
echo ========================================
echo.
echo Opening Multi-Network Dashboard...
echo Monitor multiple WiFi networks simultaneously!
echo.

timeout /t 2 /nobreak > nul

start http://localhost:3000/multi

echo.
echo ✓ Dashboard opened in your browser
echo.
echo Features:
echo   - Click on any network to monitor it
echo   - Select multiple networks at once
echo   - Each gets its own real-time graph
echo   - Click again to remove
echo.
echo ========================================
