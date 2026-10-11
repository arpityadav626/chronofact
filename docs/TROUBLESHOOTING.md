# CHRONOFACT Troubleshooting Guide

## Error Messages & Solutions

### "Operator credentials are not configured"

**Cause**: Environment variables not set

**Solution:**
```powershell
# Set variables and restart terminal
set CHRONOFACT_USER=examiner
set CHRONOFACT_PASSWORD=SecurePassMin16Chars!
set CHRONOFACT_AUDIT_KEY=audit-key-min-32-chars
set CHRONOFACT_VAULT_KEY_B64=your-32-byte-key
```

**Verify:**
```powershell
echo %CHRONOFACT_USER%
echo %CHRONOFACT_PASSWORD%
```

### "Vault key must decode to exactly 32 bytes"

**Cause**: Invalid base64 or wrong key size

**Solution:**
```powershell
# Generate correct key
python -c "import base64,secrets; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"
```

### Port already in use (Error: Address already in use)

**Cause**: Another process using port 8007

**Solution:**
```powershell
# Find and kill process on port 8007
netstat -ano | findstr :8007
taskkill /F /PID <process_id>

# Or use different port
python -m uvicorn app.main:app --host 127.0.0.1 --port 8008
```

### "Could not find mmls.exe"

**Cause**: Sleuth Kit not in PATH

**Solution:**
```powershell
# Option 1: Add to PATH
set PATH=C:\Users\antriksh\Downloads\sleuthkit-4.14.0-win32\sleuthkit-4.14.0-win32\bin;%PATH%

# Option 2: Pass explicit path
python phase3_disk.py --tsk-bin "C:\Path\To\bin" ...
```

### "Could not find Volatility 3 command"

**Cause**: Volatility 3 not extracted or in wrong location

**Solution:**
```powershell
# Extract zip manually (required due to earlier extraction failure)
# Place vol.exe in: C:\Users\antriksh\Downloads\volatility3

# Verify
C:\Users\antriksh\Downloads\volatility3\vol.exe --help

# Run with explicit path
python phase4_memory.py --vol-bin "C:\Users\antriksh\Downloads\volatility3" ...
```

### "ImportError: cannot import name"

**Cause**: Module not installed or venv not activated

**Solution:**
```powershell
# Activate venv and install
venv\Scripts\activate
pip install -r requirements.txt

# Verify installation
python -c "import reportlab; print(reportlab.__version__)"
```

### "OperationalError: no such table"

**Cause**: Database not initialized or corrupted

**Solution:**
```powershell
# Check if database exists
dir chronofact-data\chronofact.sqlite3

# If missing, restart server (init_db runs on startup)
# If corrupted, restore from backup
```

### "HTTP 403: Insufficient role"

**Cause**: Trying to access endpoint without operator authentication

**Solution:**
```powershell
# Add authentication to curl
curl -u examiner:SecurePassMin16Chars! http://127.0.0.1:8007/api/evidence
```

---

## Common Issues

### Database not found
```powershell
# Check path
dir chronofact-data\chronofact.sqlite3

# Verify environment variable
echo %CHRONOFACT_DATA_DIR%
```

### Vault encryption/decryption failed
```powershell
# Verify vault key is correct length
python -c "import base64; print(len(base64.urlsafe_b64decode('YOUR_KEY')))"
# Should output: 32

# If wrong, regenerate and restart server
```

### Upload size limit exceeded
**Default**: 50MB
**Change**: Edit `MAX_UPLOAD_BYTES` in `app/main.py`

### Report generation fails
```powershell
# Check file permissions
dir /Q chronofact-data\chronofact.sqlite3

# Run as administrator if permission denied

# Verify database integrity
python -c "import sqlite3; conn = sqlite3.connect('chronofact-data/chronofact.sqlite3'); print('OK')"
```

### Model training fails
```powershell
# Check CSV format
python -c "import pandas as pd; df = pd.read_csv('training.csv'); print(df.columns.tolist())"

# Required columns: event_id, scenario_id, timestamp, source, action, bytes, label

# Check group count
python -c "import pandas as pd; df = pd.read_csv('training.csv'); print(df.scenario_id.nunique())"
# Must be >= 4
```

### Volatility plugin errors
```powershell
# Try offline mode (default)
python phase4_memory.py --offline

# If symbols needed, allow downloads
python phase4_memory.py --allow-symbol-download

# Check plugin output
type output\memory-run-*/plugins/windows.pslist\stdout.txt
```

---

## Verification Commands

### System Check
```powershell
# Python version
python --version

# Dependencies
venv\Scripts\pip list

# Environment variables
set CHRONOFACT
```

### Server Check
```powershell
# Health
curl http://127.0.0.1:8007/

# Auth
curl -u examiner:SecurePassMin16Chars! http://127.0.0.1:8007/api/evidence

# Integrity
curl -u examiner:SecurePassMin16Chars! http://127.0.0.1:8007/api/integrity/verify
```

### External Tools
```powershell
# Sleuth Kit
mmls.exe -V

# Volatility (if installed)
C:\Users\antriksh\Downloads\volatility3\vol.exe --help
```

---

## Support Contacts

| Issue | Contact |
|-------|---------|
| Installation | See SETUP.md |
| Usage | See USAGE.md |
| Security | See SECURITY.md |
| Operations | See OPERATIONAL.md |
| Legal/Agency | Your agency forensic lab |

---

**Version**: 2.0.0 | **Date**: 2026-10-11
