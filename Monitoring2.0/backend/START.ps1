#!/usr/bin/env pwsh
# Monitoring System 2.0 - Complete Startup Script for PowerShell
# This script will set up and run the entire monitoring system

Clear-Host
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  MONITORING SYSTEM 2.0 - STARTUP SCRIPT" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if in backend folder
if (-not (Test-Path "main.py")) {
    Write-Host "Error: Please run this script from the backend folder" -ForegroundColor Red
    Write-Host "Navigate to: C:\Users\AMUDHAN.M\Monitoring2.0\backend" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if requirements are installed
try {
    python -c "import fastapi" 2>&1 | Out-Null
} catch {
    Write-Host ""
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to install dependencies" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}
Write-Host "✓ Dependencies installed" -ForegroundColor Green

# Check .env file
if (-not (Test-Path ".env")) {
    Write-Host ""
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host ""
    Write-Host "⚠️  IMPORTANT: Please add your Groq API key to .env file" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Open the .env file in this folder" -ForegroundColor White
    Write-Host "2. Find: GROQ_API_KEY=your_groq_api_key_here" -ForegroundColor White
    Write-Host "3. Replace with your actual key from https://console.groq.com" -ForegroundColor White
    Write-Host "4. Save the file" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter when done"
}
Write-Host "✓ Configuration ready" -ForegroundColor Green

# Create logs directory
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
}
Write-Host "✓ Logs directory ready" -ForegroundColor Green

# Start the server
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  STARTING MONITORING SYSTEM..." -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Server will run on: http://localhost:8000" -ForegroundColor Yellow
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""
Write-Host "To run tests in another terminal:" -ForegroundColor White
Write-Host "  python test_api.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python main.py
