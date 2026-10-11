# CHRONOFACT Complete Setup Guide

## Current Setup Status

✅ **All Phases Integrated** (0-6)

| Phase | Description | Status |
|-------|-------------|--------|
| 0 | Security patches | ✅ Integrated |
| 1 | Encrypted vault | ✅ AES-GCM |
| 2 | Read-only parsers | ✅ CSV/TXT/SQLite/EVTX/Registry |
| 3 | Disk analysis | ✅ Sleuth Kit v4.14.0 |
| 4 | Memory analysis | ✅ Volatility 3 wrapper |
| 5 | Report generation | ✅ DOCX/PDF/HTML/CSV |
| 6 | ML training | ✅ Grouped-holdout |

## Location

```
C:\Users\antriksh\Downloads\arpit_hackathon\chronofact_installed\chronofact\
```

## External Tools Installed

- **Sleuth Kit v4.14.0**: `C:\Users\antriksh\Downloads\sleuthkit-4.14.0-win32\sleuthkit-4.14.0-win32\bin`
- **Volatility 3**: Install separately (see below)

## Quick Start

### 1. Start Server
```powershell
cd C:\Users\antriksh\Downloads\arpit_hackathon\chronofact_installed\chronofact
START_FULL.bat
```

Server runs on `http://127.0.0.1:8007`

**Credentials**: `examiner` / `SecurePassMin16Chars!`

### 2. Upload Evidence
```powershell
curl -u examiner:SecurePassMin16Chars! ^
  -F "file=@C:\path\to\evidence.csv" ^
  -F "case_id=CASE-001" ^
  http://127.0.0.1:8007/api/evidence
```

### 3. Generate Report
```powershell
python phase5_report.py ^
  --db ./chronofact-data/chronofact.sqlite3 ^
  --case-id CASE-001 ^
  --examiner examiner1 ^
  --output-root ./reports
```

## Tool Usage Examples

### Phase 3: Disk Analysis
```powershell
python phase3_disk.py ^
  --image "C:\path\to\image.dd" ^
  --output-root "./output" ^
  --case-id "CASE-001" ^
  --examiner "examiner1" ^
  --acquisition-reference "REF-001" ^
  --write-blocker-statement "Test image" ^
  inspect
```

### Phase 4: Memory Analysis (requires Volatility 3)
Install Volatility 3:
```powershell
pip install volatility3
```

Then run:
```powershell
python phase4_memory.py ^
  --memory-image "C:\path\to\dump.raw" ^
  --output-root "./output" ^
  --case-id "CASE-001" ^
  --examiner "examiner1" ^
  --acquisition-reference "REF-001" ^
  --acquisition-note "Test memory"
```

### Phase 5: Report Generation
```powershell
python phase5_report.py ^
  --db ./chronofact-data/chronofact.sqlite3 ^
  --case-id CASE-001 ^
  --examiner examiner1 ^
  --findings-json ./findings.json ^
  --output-root ./reports
```

### Phase 6: ML Training
```powershell
python phase6_ml.py train ^
  --input "./training.csv" ^
  --output-root "./model-runs" ^
  --group-column "scenario_id" ^
  --label-column "label" ^
  --positive-label-definition "Reviewed target events"
```

## Environment Variables

Set in `.env` or PowerShell:
```powershell
set CHRONOFACT_USER=examiner
set CHRONOFACT_PASSWORD=SecurePassMin16Chars!
set CHRONOFACT_AUDIT_KEY=audit-key-min-32-chars
set CHRONOFACT_VAULT_KEY_B64=kUPIpkwEMr_-jsbuvNfCUdZIrAXE1X0OhNXhSt-tL08=
set CHRONOFACT_DATA_DIR=./chronofact-data
```

## Important Notes

- **Security**: Never commit `.env` or keys to Git
- **Legal**: Requires agency approval for operational use
- **Forensics**: Use hardware write-blockers for real acquisitions
- **Volatility**: Must be installed separately (not included)
- **Sleuth Kit**: Already configured at v4.14.0

## Verification

Check server is running:
```powershell
curl http://127.0.0.1:8007/
```

Check integrity:
```powershell
curl -u examiner:SecurePassMin16Chars! http://127.0.0.1:8007/api/integrity/verify
```

---
**Version**: 2.0.0 | **Date**: 2026-10-11
