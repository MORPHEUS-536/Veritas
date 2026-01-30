#!/bin/bash
# Quick Setup Script for Veritas Backend with NeonDB PostgreSQL
# Run this script after updating DATABASE_URL in .env

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║ Veritas Backend Setup - PostgreSQL via NeonDB            ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

echo "[1] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found. Please install Python 3.8+"
    exit 1
fi
python3 --version
echo "OK - Python found"

echo ""
echo "[2] Installing dependencies for Monitoring2.0..."
cd Monitoring2.0/backend
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install Monitoring2.0 dependencies"
    exit 1
fi
echo "OK - Monitoring2.0 dependencies installed"
cd ../..

echo ""
echo "[3] Installing dependencies for staffstuddash..."
cd staffstuddash/backend
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install staffstuddash dependencies"
    exit 1
fi
echo "OK - staffstuddash dependencies installed"
cd ../..

echo ""
echo "[4] Installing dependencies for dropout..."
cd dropout
pip install sqlalchemy>=2.0.0 psycopg2-binary>=2.9.0 python-dotenv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dropout dependencies"
    exit 1
fi
echo "OK - dropout dependencies installed"
cd ..

echo ""
echo "[5] Verifying database connections..."
python3 verify_database.py
if [ $? -ne 0 ]; then
    echo "WARNING: Some database tests failed"
    echo "Please check your .env configuration"
    exit 1
fi

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║ Setup Complete!                                           ║"
echo "║                                                            ║"
echo "║ Next Steps:                                                ║"
echo "║ 1. Ensure DATABASE_URL is set correctly in .env           ║"
echo "║ 2. Start your backend: python3 main.py                    ║"
echo "║ 3. Check DATABASE_SETUP.md for detailed documentation    ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
