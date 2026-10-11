# CHRONOFACT Setup Guide

## System Requirements

- **OS**: Windows 10/11
- **Python**: 3.10 or higher
- **RAM**: 8GB minimum (16GB recommended for memory analysis)
- **Disk**: 20GB free space minimum

---

## Installation Steps

### 1. Clone/Download Project
Project location: `C:\Users\antriksh\Downloads\arpit_hackathon\chronofact_installed\chronofact`

### 2. Install Python Dependencies
```powershell
cd C:\Users\antriksh\Downloads\arpit_hackathon\chronofact_installed\chronofact
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create/edit `.env` file in project root:
```env
CHRONOFACT_USER=examiner
CHRONOFACT_PASSWORD=SecurePassMin16Chars!
CHRONOFACT_AUDIT_KEY=audit-key-min-32-chars-secure
CHRONOFACT_VAULT_KEY_B64=kUPIpkwEMr_-jsbuvNfCUdZIrAXE1X0OhNXhSt-tL08=
CHRONOFACT_DATA_DIR=./chronofact-data
```

**Important**: 
- Password must be at least 16 characters
- Vault key must be 32 bytes (base64 encoded)
- **Never commit `.env` to Git**

### 4. External Tools Setup

#### Sleuth Kit (Phase 3)
**Already installed** at:
`C:\Users\antriksh\Downloads\sleuthkit-4.14.0-win32\sleuthkit-4.14.0-win32\bin`

Tools available: `mmls.exe`, `tsk_recover.exe`, `fls.exe`, `icat.exe`

#### Volatility 3 (Phase 4)
**✅ Now installed and working:**
- Path: `C:\Users\antriksh\Downloads\volatility3`
- Files: `vol.exe` (22MB) ready to use

**To verify installation:**
```powershell
C:\Users\antriksh\Downloads\volatility3\vol.exe --help
```

---

## Starting the Server

### Option 1: Full Start (with Sleuth Kit PATH)
```powershell
START_FULL.bat
```

### Option 2: Manual Start
```powershell
cd C:\Users\antriksh\Downloads\arpit_hackathon\chronofact_installed\chronofact
venv\Scripts\activate
set CHRONOFACT_USER=examiner
set CHRONOFACT_PASSWORD=SecurePassMin16Chars!
set CHRONOFACT_AUDIT_KEY=audit-key-min-32-chars
set CHRONOFACT_VAULT_KEY_B64=kUPIpkwEMr_-jsbuvNfCUdZIrAXE1X0OhNXhSt-tL08=
python -m uvicorn app.main:app --host 127.0.0.1 --port 8007
```

Server runs at: **http://127.0.0.1:8007**

---

## Verification

### Check Server is Running
```powershell
curl http://127.0.0.1:8007/
```

### Check Authentication
```powershell
curl -u examiner:SecurePassMin16Chars! http://127.0.0.1:8007/api/evidence
```

### Check Vault Integrity
```powershell
curl -u examiner:SecurePassMin16Chars! http://127.0.0.1:8007/api/integrity/verify
```

### Check Sleuth Kit
```powershell
python phase3_disk.py --image "C:\test.raw" --output-root "./test" --case-id "TEST" --examiner "test" --acquisition-reference "TEST" --write-blocker-statement "TEST" inspect 2>&1 | findstr "Could not find"
```
If successful, you should see error about missing image, NOT missing mmls.exe.

---

## Troubleshooting

### "Operator credentials not configured"
- Ensure `.env` exists AND environment variables are set
- Restart terminal after setting variables

### "Vault key not configured"
- Check `CHRONOFACT_VAULT_KEY_B64` is 32 bytes when decoded
- Generate new key with: `python -c "import base64,secrets; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"`

### Port already in use
- Change port in `uvicorn` command
- Kill existing process: `taskkill /F /PID <process_id>`

### "mmls.exe not found"
- Install Sleuth Kit manually
- Pass path to script: `--tsk-bin "C:\Path\To\bin"`

### "vol.exe not found"
- Manually extract Volatility 3 zip
- Ensure `vol.exe` is in extraction directory
- Pass path to script: `--vol-bin "C:\Path\To\volatility3"`

---

## Backup & Recovery

### Backup Vault Key
```powershell
# Save vault key to secure location
echo kUPIpkwEMr_-jsbuvNfCUdZIrAXE1X0OhNXhSt-tL08= > C:\backup\vault-key.txt
# Encrypt this file with Windows BitLocker or similar
```

### Backup Database
```powershell
robocopy C:\Users\antriksh\Downloads\arpit_hackathon\chronofact_installed\chronofact\chronofact-data C:\backup\chronofact-data /MIR
```

### Recovery Steps
1. Restore `.env` with same vault key
2. Restore database files
3. Start server
4. Verify integrity with `/api/integrity/verify`

---

**Version**: 2.0.0 | **Date**: 2026-10-11
