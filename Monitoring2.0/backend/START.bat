@echo off
REM Monitoring System 2.0 - Complete Startup Script for Windows
REM This script will set up and run the entire monitoring system

cls
echo.
echo ============================================================
echo   MONITORING SYSTEM 2.0 - STARTUP SCRIPT
echo ============================================================
echo.

REM Check if in backend folder
if not exist "main.py" (
    echo Error: Please run this script from the backend folder
    echo Navigate to: C:\Users\AMUDHAN.M\Monitoring2.0\backend
    echo.
    pause
    exit /b 1
)

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)
echo ✓ Python found

REM Check if requirements are installed
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo.
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
)
echo ✓ Dependencies installed

REM Check .env file
if not exist ".env" (
    echo.
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo ⚠️  IMPORTANT: Please add your Groq API key to .env file
    echo.
    echo 1. Open the .env file in this folder
    echo 2. Find: GROQ_API_KEY=your_groq_api_key_here
    echo 3. Replace with your actual key from https://console.groq.com
    echo 4. Save the file
    echo.
    pause
)
echo ✓ Configuration ready

REM Create logs directory
if not exist "logs" mkdir logs
echo ✓ Logs directory ready

REM Start the server
echo.
echo ============================================================
echo   STARTING MONITORING SYSTEM...
echo ============================================================
echo.
echo Server will run on: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo To run tests in another terminal:
echo   python test_api.py
echo.
echo Press Ctrl+C to stop the server
echo.

python main.py
