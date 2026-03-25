@echo off
REM ============================================================================
REM START_SERVER.BAT - Quick start script for URL Shortener
REM ============================================================================
REM This batch file makes it easy to start the URL shortener server
REM Just double-click this file or run it from PowerShell/CMD
REM ============================================================================

echo.
echo ========================================
echo   URL Shortener - Starting Server
echo ========================================
echo.

REM Check if we're in the correct directory
if not exist "app\main.py" (
    echo ERROR: Cannot find app\main.py
    echo Please run this script from the project root directory
    echo Expected location: C:\Users\USER\training\1603\
    echo.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found
    echo Please create a virtual environment first:
    echo   python -m venv venv
    echo   venv\Scripts\pip.exe install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Check if dependencies are installed
venv\Scripts\python.exe -c "import fastapi" 2>nul
if errorlevel 1 (
    echo WARNING: FastAPI not installed
    echo Installing dependencies...
    echo.
    venv\Scripts\pip.exe install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
    echo.
    echo Dependencies installed successfully!
    echo.
)

REM Create data directory if it doesn't exist
if not exist "data" (
    echo Creating data directory...
    mkdir data
)

echo Starting URL Shortener...
echo.
echo Server will be available at:
echo   - API Docs:  http://127.0.0.1:8000/docs
echo   - ReDoc:     http://127.0.0.1:8000/redoc
echo   - Database:  http://127.0.0.1:8000/admin/database
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM Start the server
venv\Scripts\uvicorn.exe app.main:app --reload

REM If the server stops, pause so user can see any error messages
echo.
echo Server stopped.
pause
