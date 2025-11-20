@echo off
setlocal enableextensions

REM Change to the directory of this script
cd /d "%~dp0"

REM Create venv if missing
if not exist venv (
  echo Creating Python virtual environment...
  py -3 -m venv venv
)

REM Activate venv
call "%~dp0venv\Scripts\activate.bat"

REM Ensure dependencies are installed
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

REM Run the app
python soulnote_complete.py

endlocal
