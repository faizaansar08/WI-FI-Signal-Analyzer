# Wi-Fi Signal Strength Analyzer - Startup Script
# PowerShell script to launch the application

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Wi-Fi Signal Strength Analyzer" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found! Please install Python 3.8+" -ForegroundColor Red
    Write-Host "Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host ""

# Check if requirements are installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
$requirementsFile = Join-Path $PSScriptRoot "requirements.txt"

if (Test-Path $requirementsFile) {
    Write-Host "Installing/Updating dependencies..." -ForegroundColor Yellow
    pip install -r $requirementsFile --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
    } else {
        Write-Host "⚠ Some dependencies may have issues" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠ requirements.txt not found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Wi-Fi Signal Analyzer Server..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Dashboard will be available at:" -ForegroundColor Yellow
Write-Host "  → http://localhost:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the Flask application
python app.py
