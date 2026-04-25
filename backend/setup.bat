@echo off
REM Setup script for Smart Banking Assistant Backend
REM Run this to set up the project automatically

echo ============================================
echo Smart Banking Assistant - Setup Script
echo ============================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/5] Python found
python --version

REM Create virtual environment
echo.
echo [2/5] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)

REM Activate virtual environment
echo.
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo [4/5] Installing Python packages...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

REM Create .env file if it doesn't exist
echo.
echo [5/5] Setting up environment variables...
if not exist ".env" (
    copy .env.example .env
    echo .env file created from .env.example
    echo Please edit .env with your database credentials
) else (
    echo .env file already exists
)

echo.
echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo Next Steps:
echo 1. Edit .env file with your MySQL credentials
echo 2. Import schema.sql into your MySQL database
echo 3. Run: uvicorn main:app --reload
echo.
echo Press any key to exit...
pause >nul
