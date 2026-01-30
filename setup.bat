@echo off
REM Quick Setup Script for Veritas Backend with NeonDB PostgreSQL
REM Run this script after updating DATABASE_URL in .env

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║ Veritas Backend Setup - PostgreSQL via NeonDB            ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

echo [1] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+
    pause
    exit /b 1
)
echo OK - Python found

echo.
echo [2] Installing dependencies for Monitoring2.0...
cd Monitoring2.0\backend
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo ERROR: Failed to install Monitoring2.0 dependencies
    pause
    exit /b 1
)
echo OK - Monitoring2.0 dependencies installed
cd ..\..

echo.
echo [3] Installing dependencies for staffstuddash...
cd staffstuddash\backend
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo ERROR: Failed to install staffstuddash dependencies
    pause
    exit /b 1
)
echo OK - staffstuddash dependencies installed
cd ..\..

echo.
echo [4] Installing dependencies for dropout...
cd dropout
pip install sqlalchemy>=2.0.0 psycopg2-binary>=2.9.0 python-dotenv >nul 2>&1
if errorlevel 1 (
    echo ERROR: Failed to install dropout dependencies
    pause
    exit /b 1
)
echo OK - dropout dependencies installed
cd ..

echo.
echo [5] Verifying database connections...
python verify_database.py
if errorlevel 1 (
    echo WARNING: Some database tests failed
    echo Please check your .env configuration
    pause
    exit /b 1
)

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║ Setup Complete!                                           ║
echo ║                                                            ║
echo ║ Next Steps:                                                ║
echo ║ 1. Ensure DATABASE_URL is set correctly in .env           ║
echo ║ 2. Start your backend: python main.py                     ║
echo ║ 3. Check DATABASE_SETUP.md for detailed documentation    ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

pause
