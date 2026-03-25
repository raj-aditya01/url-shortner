# ============================================================================
# START_SERVER.PS1 - PowerShell script to start URL Shortener
# ============================================================================
# This script makes it easy to start the URL shortener server
# Run from PowerShell: .\start_server.ps1
# ============================================================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   URL Shortener - Starting Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the correct directory
if (-not (Test-Path "app\main.py")) {
    Write-Host "ERROR: Cannot find app\main.py" -ForegroundColor Red
    Write-Host "Please run this script from the project root directory"
    Write-Host "Expected location: C:\Users\USER\training\1603\"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if virtual environment exists
if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "ERROR: Virtual environment not found" -ForegroundColor Red
    Write-Host "Please create a virtual environment first:"
    Write-Host "  python -m venv venv"
    Write-Host "  .\venv\Scripts\pip.exe install -r requirements.txt"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if dependencies are installed
try {
    $null = .\venv\Scripts\python.exe -c "import fastapi" 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "FastAPI not installed"
    }
} catch {
    Write-Host "WARNING: FastAPI not installed" -ForegroundColor Yellow
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    Write-Host ""
    
    .\venv\Scripts\pip.exe install -r requirements.txt
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    Write-Host ""
    Write-Host "Dependencies installed successfully!" -ForegroundColor Green
    Write-Host ""
}

# Create data directory if it doesn't exist
if (-not (Test-Path "data")) {
    Write-Host "Creating data directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path "data" | Out-Null
}

Write-Host "Starting URL Shortener..." -ForegroundColor Green
Write-Host ""
Write-Host "Server will be available at:" -ForegroundColor Cyan
Write-Host "  - API Docs:  " -NoNewline
Write-Host "http://127.0.0.1:8000/docs" -ForegroundColor Yellow
Write-Host "  - ReDoc:     " -NoNewline
Write-Host "http://127.0.0.1:8000/redoc" -ForegroundColor Yellow
Write-Host "  - Database:  " -NoNewline
Write-Host "http://127.0.0.1:8000/admin/database" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Start the server
try {
    .\venv\Scripts\uvicorn.exe app.main:app --reload
} catch {
    Write-Host ""
    Write-Host "Server stopped with error: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Server stopped." -ForegroundColor Yellow
Read-Host "Press Enter to exit"
