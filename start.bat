@echo off
setlocal enabledelayedexpansion
REM ======================================================================
REM  CHRONOFACT — Digital Forensic Investigation Workbench
REM  1-Click Windows Launcher (SUTRAM 2026 Round 2)
REM ======================================================================
title ChronoFact Forensic Workbench
color 0a

echo ======================================================================
echo    CHRONOFACT: Digital Forensic Investigation Workbench
echo    Bharatiya Sakshya Adhiniyam, 2023 (BSA Section 63(4))
echo ======================================================================
echo.

REM Create local secure directories if missing
if not exist "data\vault" mkdir "data\vault" 2>nul
if not exist "data\evidence_storage" mkdir "data\evidence_storage" 2>nul
if not exist "chronofact-data" mkdir "chronofact-data" 2>nul

REM Check Python presence
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python 3.10+ was not found on your system PATH!
    echo Please install Python 3.10 or higher from python.org and ensure "Add Python to PATH" is checked.
    pause
    exit /b 1
)

REM Ensure virtual environment if present
if exist "venv\Scripts\activate.bat" (
    echo Activating local Python virtual environment...
    call venv\Scripts\activate.bat
)

REM Start server via run.py
echo.
echo Starting ChronoFact Workbench at http://127.0.0.1:8000 ...
echo Press Ctrl + C in this terminal window to stop the server.
echo ======================================================================
echo.

python run.py

pause
