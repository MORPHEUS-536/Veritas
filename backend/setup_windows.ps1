# Veritas Backend Setup Script for Windows PowerShell
# Usage: .\setup_windows.ps1
# This script sets up Neon DB integration and starts the backend

param(
    [string]$DatabaseUrl = $null,
    [switch]$SkipDependencies = $false,
    [switch]$LocalDb = $false
)

function Write-Header {
    param([string]$Text)
    Write-Host ""
    Write-Host ("=" * 70) -ForegroundColor Cyan
    Write-Host "  $Text" -ForegroundColor Cyan
    Write-Host ("=" * 70) -ForegroundColor Cyan
    Write-Host ""
}

function Write-Success {
    param([string]$Text)
    Write-Host "✓ $Text" -ForegroundColor Green
}

function Write-Error {
    param([string]$Text)
    Write-Host "✗ $Text" -ForegroundColor Red
}

function Write-Info {
    param([string]$Text)
    Write-Host "ℹ $Text" -ForegroundColor Yellow
}

# Start
Write-Header "VERITAS BACKEND SETUP - WINDOWS"

# Step 1: Check Python
Write-Host "Step 1: Checking Python installation..." -ForegroundColor White

$pythonVersion = python --version 2>$null
if ($pythonVersion) {
    Write-Success "Python found: $pythonVersion"
} else {
    Write-Error "Python not found. Please install Python 3.9+ from https://www.python.org/"
    exit 1
}

# Step 2: Install dependencies
if (-not $SkipDependencies) {
    Write-Host ""
    Write-Host "Step 2: Installing dependencies..." -ForegroundColor White
    Write-Info "Installing from requirements_db.txt..."
    
    try {
        pip install -r requirements_db.txt
        Write-Success "Dependencies installed"
    } catch {
        Write-Error "Failed to install dependencies: $_"
        exit 1
    }
} else {
    Write-Host ""
    Write-Host "Step 2: Skipping dependency installation" -ForegroundColor White
}

# Step 3: Configure database connection
Write-Host ""
Write-Host "Step 3: Configuring database connection..." -ForegroundColor White

if ($LocalDb) {
    $dbUrl = "postgresql://postgres:postgres@localhost:5432/veritas_db"
    Write-Info "Using local PostgreSQL: $dbUrl"
} else {
    if (-not $DatabaseUrl) {
        Write-Host ""
        Write-Host "Enter your Neon DB connection string:" -ForegroundColor Yellow
        Write-Host "(Get it from: https://console.neon.tech > Connection string)" -ForegroundColor Gray
        Write-Host ""
        $DatabaseUrl = Read-Host "DATABASE_URL"
        
        if (-not $DatabaseUrl) {
            Write-Error "Database URL is required"
            exit 1
        }
    }
    $dbUrl = $DatabaseUrl
    Write-Info "Using Neon DB connection"
}

# Set environment variable
$env:DATABASE_URL = $dbUrl
Write-Success "DATABASE_URL set for this session"

# Persist to .env file
$envContent = "DATABASE_URL=$dbUrl`nJWT_SECRET=change-this-in-production-to-min-32-chars`nDEBUG=True"
Set-Content -Path ".\.env" -Value $envContent -Encoding UTF8
Write-Success ".env file created"

# Step 4: Initialize database
Write-Host ""
Write-Host "Step 4: Initializing database..." -ForegroundColor White

try {
    python -c "from database import init_db; init_db(); print('Database initialized')"
    Write-Success "Database schema created"
} catch {
    Write-Error "Failed to initialize database: $_"
    Write-Info "Check if Neon DB connection is valid"
    exit 1
}

# Step 5: Test connection
Write-Host ""
Write-Host "Step 5: Testing database connection..." -ForegroundColor White

$testResult = python test_neon_connection.py 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Success "Database connection verified"
} else {
    Write-Error "Database connection failed"
    Write-Info "Run: python test_neon_connection.py for details"
    exit 1
}

# Step 6: Ready to run
Write-Header "SETUP COMPLETE ✓"

Write-Host "Your Veritas backend is ready to run!" -ForegroundColor Green
Write-Host ""
Write-Host "To start the backend:" -ForegroundColor Yellow
Write-Host "  uvicorn api_routes:app --reload" -ForegroundColor White
Write-Host ""
Write-Host "Then visit:" -ForegroundColor Yellow
Write-Host "  http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "For Neon DB monitoring:" -ForegroundColor Yellow
Write-Host "  https://console.neon.tech" -ForegroundColor White
Write-Host ""

# Optional: Ask to start backend now
$response = Read-Host "Start backend now? (y/n)"
if ($response -eq "y" -or $response -eq "Y") {
    Write-Host ""
    Write-Host "Starting backend..." -ForegroundColor Green
    uvicorn api_routes:app --reload
} else {
    Write-Host ""
    Write-Host "Run 'uvicorn api_routes:app --reload' when ready" -ForegroundColor Yellow
}
