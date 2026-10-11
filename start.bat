@echo off
REM CHRONOFACT Windows Quick Start Script

echo ================================
echo CHRONOFACT Forensic Workbench
echo ================================

REM Create data directories
mkdir data 2>nul
mkdir data\vault 2>nul
mkdir data\evidence_storage 2>nul

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Install Python 3.10+
    pause
    exit /b 1
)

REM Install dependencies if needed
if not exist venv (
    echo Installing dependencies...
    python -m pip install --upgrade pip
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate
)

REM Start the application
echo Starting CHRONOFACT...
echo Open http://127.0.0.1:8000 in your browser
echo ================================

python run.py

pause
