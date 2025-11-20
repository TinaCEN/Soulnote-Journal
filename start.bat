@echo off
REM Soulnote Quick Start Script for Windows

echo ====================================
echo Soulnote - Emotional Journaling Tool
echo ====================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
echo Checking dependencies...
pip list | findstr Flask >nul
if %errorlevel% neq 0 (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo.
)

echo.
echo ====================================
echo IMPORTANT: Before starting, make sure:
echo 1. LM Studio is running on http://localhost:1234
echo 2. You have loaded a language model in LM Studio
echo 3. The local server is started in LM Studio
echo ====================================
echo.

pause

echo Starting Soulnote backend server...
echo.
echo Server will run on http://localhost:5000
echo Frontend is at: frontend/index.html
echo.
echo Press Ctrl+C to stop the server
echo.

python backend/app.py
