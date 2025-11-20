#!/bin/bash
# Soulnote Quick Start Script for macOS/Linux

echo "===================================="
echo "Soulnote - Emotional Journaling Tool"
echo "===================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! pip list | grep -q Flask; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    echo ""
fi

echo ""
echo "===================================="
echo "IMPORTANT: Before starting, make sure:"
echo "1. LM Studio is running on http://localhost:1234"
echo "2. You have loaded a language model in LM Studio"
echo "3. The local server is started in LM Studio"
echo "===================================="
echo ""

read -p "Press Enter to continue..."

echo "Starting Soulnote backend server..."
echo ""
echo "Server will run on http://localhost:5000"
echo "Frontend is at: frontend/index.html"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python backend/app.py
