@echo off
title CHRONOFACT - Digital Forensic Workbench
echo ======================================================================
echo          Starting CHRONOFACT Digital Forensic Workbench...
echo ======================================================================
echo.
cd /d "%~dp0"

REM Try default python, fallback to installed Python 3.12 path
where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    python run.py
) else (
    if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
        "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" run.py
    ) else (
        echo [ERROR] Python 3.12 not found! Please ensure Python is installed.
        pause
    )
)
pause
