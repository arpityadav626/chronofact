@echo off
REM CHRONOFACT Complete Start Script

REM Set PATH to include Sleuth Kit and Volatility
set PATH=C:\Users\antriksh\Downloads\sleuthkit-4.14.0-win32\sleuthkit-4.14.0-win32\bin;%PATH%

REM Set required environment variables
set CHRONOFACT_USER=examiner
set CHRONOFACT_PASSWORD=SecurePassMin16Chars!
set CHRONOFACT_AUDIT_KEY=audit-key-min-32-chars-secure
set CHRONOFACT_VAULT_KEY_B64=kUPIpkwEMr_-jsbuvNfCUdZIrAXE1X0OhNXhSt-tL08=
set CHRONOFACT_DATA_DIR=%CD%\chronofact-data

echo ========================================
echo CHRONOFACT Secure Workbench
echo ========================================
echo Port: 8007
echo Credentials: examiner / SecurePassMin16Chars!
echo Path: %PATH%
echo ========================================

venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8007

pause