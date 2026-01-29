#!/bin/bash

# Veritas Backend Setup Script for Linux/Mac
# Usage: chmod +x setup.sh && ./setup.sh
# This script sets up Neon DB integration and starts the backend

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

function print_header() {
    echo ""
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo ""
}

function print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

function print_error() {
    echo -e "${RED}✗ $1${NC}"
}

function print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Start
print_header "VERITAS BACKEND SETUP - LINUX/MAC"

# Step 1: Check Python
echo "Step 1: Checking Python installation..."

if command -v python3 &> /dev/null; then
    python_version=$(python3 --version)
    print_success "Python found: $python_version"
    python_cmd="python3"
else
    print_error "Python not found. Please install Python 3.9+ from https://www.python.org/"
    exit 1
fi

# Step 2: Check if virtual environment exists
echo ""
echo "Step 2: Checking virtual environment..."

if [ -d "venv" ]; then
    print_info "Virtual environment found"
    source venv/bin/activate
    print_success "Virtual environment activated"
else
    print_info "Creating virtual environment..."
    $python_cmd -m venv venv
    source venv/bin/activate
    print_success "Virtual environment created and activated"
fi

# Step 3: Install dependencies
echo ""
echo "Step 3: Installing dependencies..."

print_info "Installing from requirements_db.txt..."
pip install -q -r requirements_db.txt
print_success "Dependencies installed"

# Step 4: Configure database connection
echo ""
echo "Step 4: Configuring database connection..."

# Check if DATABASE_URL is already set
if [ -z "$DATABASE_URL" ]; then
    echo ""
    echo "Enter your Neon DB connection string:"
    echo "(Get it from: https://console.neon.tech > Connection string)"
    echo ""
    read -p "DATABASE_URL: " DATABASE_URL
    
    if [ -z "$DATABASE_URL" ]; then
        print_error "Database URL is required"
        exit 1
    fi
fi

# Export for current session
export DATABASE_URL="$DATABASE_URL"

# Create .env file
cat > .env << EOF
DATABASE_URL=$DATABASE_URL
JWT_SECRET=change-this-in-production-to-min-32-chars
DEBUG=True
EOF

print_success "DATABASE_URL configured"
print_success ".env file created"

# Step 5: Initialize database
echo ""
echo "Step 5: Initializing database..."

if $python_cmd -c "from database import init_db; init_db(); print('Database initialized')" 2>/dev/null; then
    print_success "Database schema created"
else
    print_error "Failed to initialize database"
    print_info "Check if Neon DB connection is valid"
    exit 1
fi

# Step 6: Test connection
echo ""
echo "Step 6: Testing database connection..."

if $python_cmd test_neon_connection.py > /dev/null 2>&1; then
    print_success "Database connection verified"
else
    print_error "Database connection failed"
    print_info "Run: python test_neon_connection.py for details"
    exit 1
fi

# Step 7: Ready to run
print_header "SETUP COMPLETE ✓"

echo "Your Veritas backend is ready to run!"
echo ""
echo -e "${YELLOW}To start the backend:${NC}"
echo "  uvicorn api_routes:app --reload"
echo ""
echo -e "${YELLOW}Then visit:${NC}"
echo "  http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}For Neon DB monitoring:${NC}"
echo "  https://console.neon.tech"
echo ""

# Optional: Ask to start backend now
read -p "Start backend now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo -e "${GREEN}Starting backend...${NC}"
    uvicorn api_routes:app --reload
else
    echo ""
    echo -e "${YELLOW}Run 'uvicorn api_routes:app --reload' when ready${NC}"
fi
