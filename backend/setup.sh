#!/bin/bash
# Setup script for Smart Banking Assistant Backend (Linux/Mac)
# Run this to set up the project automatically

echo "============================================"
echo "Smart Banking Assistant - Setup Script"
echo "============================================"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    echo "Please install Python 3.8+ from https://www.python.org/"
    exit 1
fi

echo "[1/5] Python found"
python3 --version

# Create virtual environment
echo ""
echo "[2/5] Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment created"
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "[3/5] Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "[4/5] Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install dependencies"
    exit 1
fi

# Create .env file if it doesn't exist
echo ""
echo "[5/5] Setting up environment variables..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ".env file created from .env.example"
    echo "Please edit .env with your database credentials"
else
    echo ".env file already exists"
fi

echo ""
echo "============================================"
echo "Setup Complete!"
echo "============================================"
echo ""
echo "Next Steps:"
echo "1. Edit .env file with your MySQL credentials"
echo "2. Import schema.sql into your MySQL database"
echo "3. Run: uvicorn main:app --reload"
echo ""
