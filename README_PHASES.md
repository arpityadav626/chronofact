# CHRONOFACT Implementation Guide

## Overview
This implements the CHRONOFACT forensic workbench with Phases 0-6.

- **Phase 0**: Security patches (auth required, no fake data)
- **Phase 1**: Evidence security backend (API at port 8003)
- **Phase 2**: Read-only parsers (SQLite, EVTX, Registry, CSV, JSONL)
- **Phase 3**: Disk image analysis (CLI)
- **Phase 4**: Memory analysis (CLI, requires Volatility 3)
- **Phase 5**: Report generation (CLI)
- **Phase 6**: ML training/score (CLI)

## Setup

```powershell
cd C:\Users\antriksh\Downloads\arpit_hackathon\chronofact_installed\chronofact
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Environment Variables

```powershell
$env:CHRONOFACT_USER = "examiner"
$env:CHRONOFACT_PASSWORD = "your-secure-password-min-16-chars"
```

## Starting the API Server

```powershell
python run.py
```

Server runs at http://127.0.0.1:8003

## CLI Tools

### Phase 3: Disk Analysis
```powershell
python phase3_disk.py --image "path/to/raw.dd" --output-root "./output" --case-id "CASE-001" --examiner "examiner1" --acquisition-reference "REF-001" --write-blocker-statement "Test image" inspect
```

### Phase 4: Memory Analysis (requires Volatility 3)
```powershell
python phase4_memory.py --memory-image "path/to/dump.raw" --output-root "./output" --case-id "CASE-001" --examiner "examiner1" --acquisition-reference "REF-001" --acquisition-note "Test memory image"
```

### Phase 5: Report Generation
```powershell
python phase5_report.py --db "./phase1-data/phase1.sqlite3" --case-id "CASE-001" --examiner "examiner1" --findings-json "./findings.json" --output-root "./reports"
```

### Phase 6: ML Training
```powershell
python phase6_ml.py train --input "./training.csv" --output-root "./model-runs" --group-column "scenario_id" --label-column "label" --positive-label-definition "Reviewed event meets target criteria"
```

## Safety Notes
- Phase 1-2 are integrated into the API
- Phases 3-6 are CLI tools for offline analysis
- Always use synthetic/test data first
- Do not use on live devices without proper procedures
- Keep credentials and vault keys secure
