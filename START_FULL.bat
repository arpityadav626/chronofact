@echo off
setlocal enabledelayedexpansion
REM ======================================================================
REM  CHRONOFACT — Digital Forensic Investigation Workbench
REM  SUTRAM 2026 Round 2 Submission (ISEA / IGDTUW)
REM ======================================================================
title ChronoFact Secure Forensic Workbench
color 0b

echo ======================================================================
echo    CHRONOFACT: Digital Forensic Investigation Workbench
echo    Bharatiya Sakshya Adhiniyam, 2023 (BSA Section 63(4))
echo ======================================================================
echo.

REM Optional: Add local tools directory if present
if exist "%CD%\tools\sleuthkit\bin" (
    set "PATH=%CD%\tools\sleuthkit\bin;!PATH!"
)

REM Set production / forensic environment defaults
if not defined CHRONOFACT_USER set CHRONOFACT_USER=examiner
if not defined CHRONOFACT_PASSWORD set CHRONOFACT_PASSWORD=SecurePassMin16Chars!
if not defined CHRONOFACT_DEMO_MODE set CHRONOFACT_DEMO_MODE=true
if not defined CHRONOFACT_AUDIT_KEY set CHRONOFACT_AUDIT_KEY=audit-key-min-32-chars-secure
if not defined CHRONOFACT_VAULT_KEY_B64 set CHRONOFACT_VAULT_KEY_B64=kUPIpkwEMr_-jsbuvNfCUdZIrAXE1X0OhNXhSt-tL08=
if not defined CHRONOFACT_DATA_DIR set CHRONOFACT_DATA_DIR=%CD%\chronofact-data

if not exist "%CHRONOFACT_DATA_DIR%" mkdir "%CHRONOFACT_DATA_DIR%"

echo  [+] Host: http://127.0.0.1:8000
echo  [+] Default User: %CHRONOFACT_USER%
echo  [+] Audit Vault: %CHRONOFACT_DATA_DIR%
echo ======================================================================
echo.

REM Check Python command
set PYTHON_CMD=python
if exist "venv\Scripts\python.exe" (
    set PYTHON_CMD=venv\Scripts\python.exe
)

echo Starting FastAPI forensic server...
%PYTHON_CMD% -m uvicorn app.main:app --host 127.0.0.1 --port 8000

if %ERRORLEVEL% neq 0 (
    echo.
    echo [!] Server exited or failed to start. Falling back to run.py launcher...
    %PYTHON_CMD% run.py
)

pause