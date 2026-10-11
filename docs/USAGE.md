# CHRONOFACT Usage Guide

## Table of Contents
1. [API Usage](#api-usage) - Phase 0-2
2. [Disk Analysis](#disk-analysis) - Phase 3
3. [Memory Analysis](#memory-analysis) - Phase 4
4. [Report Generation](#report-generation) - Phase 5
5. [ML Training](#ml-training) - Phase 6

---

## API Usage (Phases 0-2)

### Base URL
`http://127.0.0.1:8007`

### Authentication
All API endpoints require HTTP Basic Auth:
```powershell
curl -u examiner:SecurePassMin16Chars! <endpoint>
```

### Endpoints

#### POST /api/evidence
Upload encrypted exhibit.

**Request:**
```powershell
curl -u examiner:SecurePassMin16Chars! ^
  -F "file=@C:\path\to\logs.csv" ^
  -F "case_id=CASE-001" ^
  -F "notes=System access logs from workstation" ^
  http://127.0.0.1:8007/api/evidence
```

**Response:**
```json
{
  "id": "EV-9F51C8",
  "case_id": "CASE-001",
  "original_name": "logs.csv",
  "byte_size": 277,
  "sha256": "c5153b32d491cc521a07116172f5b38a5aac2004027dd66c45af9b32817b47f4",
  "sha3_256": "bfda748567b94825ddbd8f10fd6302487d73d0061537ecc9741f74ca748d8600",
  "received_at": "2026-10-11T00:00:00Z",
  "warning": "These hashes identify the bytes received by this service; they do not verify device acquisition or provenance."
}
```

#### GET /api/evidence
List all exhibits or filter by case_id.

```powershell
curl -u examiner:SecurePassMin16Chars! http://127.0.0.1:8007/api/evidence?case_id=CASE-001
```

#### GET /api/evidence/{id}/parse
Parse uploaded evidence (CSV/TXT only).

```powershell
curl -u examiner:SecurePassMin16Chars! http://127.0.0.1:8007/api/evidence/EV-9F51C8/parse
```

#### GET /api/integrity/verify
Verify vault integrity.

```powershell
curl -u examiner:SecurePassMin16Chars! http://127.0.0.1:8007/api/integrity/verify
```

**Response:**
```json
{
  "audit_entries_checked": 1,
  "evidence_files_checked": 1,
  "audit_issues": [],
  "evidence_issues": [],
  "valid": true,
  "important_limit": "This verifies local stored bytes and the keyed audit chain. It does not establish source-device authenticity, trusted time, or protection against an administrator who controls the host and key."
}
```

---

## Disk Analysis (Phase 3)

### Prerequisites
- Raw disk image (.dd, .img, or .raw)
- The Sleuth Kit installed
- **Do not use on live physical devices**

### Inspect Disk Image
```powershell
python phase3_disk.py ^
  --image "C:\path\to\disk_image.dd" ^
  --output-root "./output" ^
  --case-id "CASE-001" ^
  --examiner "examiner1" ^
  --acquisition-reference "ACQ-001" ^
  --write-blocker-statement "Used hardware write blocker Model XYZ" ^
  inspect
```

**Outputs:**
- `output/disk-run-*/manifest.json` - Run metadata with hash verification
- `output/disk-run-*/partition_layout.stdout.txt` - Partition table

### Recover Files from Unallocated Space
```powershell
python phase3_disk.py ^
  --image "C:\path\to\disk_image.dd" ^
  --output-root "./output" ^
  --case-id "CASE-001" ^
  --examiner "examiner1" ^
  --acquisition-reference "ACQ-001" ^
  --write-blocker-statement "Used hardware write blocker Model XYZ" ^
  recover ^
  --offset-sectors 2048 ^
  --include-allocated
```

**Outputs:**
- `output/disk-run-*/recovered/` - Recovered files
- `output/disk-run-*/recovered_files.jsonl` - Hashed file list
- `output/disk-run-*/manifest.json` - Run verification

### Notes
- `offset-sectors` is obtained from partition layout output
- Hash verification happens before and after processing
- Manifest includes both SHA-256 and SHA-3-256

---

## Memory Analysis (Phase 4)

### Prerequisites
- Memory dump (raw, .raw, or .bin)
- Volatility 3 installed
- **Manual extraction required** (zip extraction failed during setup)

### Run Memory Analysis
```powershell
python phase4_memory.py ^
  --memory-image "C:\path\to\memory_dump.raw" ^
  --output-root "./output" ^
  --case-id "CASE-001" ^
  --examiner "examiner1" ^
  --acquisition-reference "MEM-001" ^
  --acquisition-note "Acquired with DumpIt v4.5" ^
  --vol-bin "C:\Users\antriksh\Downloads\volatility3"
```

**Default Plugins:**
- `windows.info` - System information
- `windows.pslist` - Process list
- `windows.pstree` - Process tree
- `windows.cmdline` - Command line arguments
- `windows.netscan` - Network connections
- `windows.dlllist` - Loaded DLLs
- `windows.filescan` - File system scan
- `windows.registry.hivelist` - Registry hives

### Custom Plugins
```powershell
python phase4_memory.py ^
  --memory-image "C:\path\to\memory_dump.raw" ^
  --output-root "./output" ^
  --case-id "CASE-001" ^
  --examiner "examiner1" ^
  --acquisition-reference "MEM-001" ^
  --acquisition-note "Acquired with DumpIt v4.5" ^
  --vol-bin "C:\Users\antriksh\Downloads\volatility3" ^
  --plugins windows.pslist windows.cmdline windows.netscan
```

### Offline Mode (Default)
```powershell
# Default - no symbol downloads
python phase4_memory.py ...

# Allow symbol downloads (if needed)
python phase4_memory.py ... --allow-symbol-download
```

### Outputs
- `output/memory-run-*/manifest.json` - Run metadata
- `output/memory-run-*/plugins/plugin_name/stdout.txt` - Plugin output
- `output/memory-run-*/manifest.json.sha256` - Manifest hash

---

## Report Generation (Phase 5)

### Prerequisites
- Evidence in database (`chronofact.sqlite3`)
- Optional: Examiner findings in JSON format

### Generate Basic Report
```powershell
python phase5_report.py ^
  --db "./chronofact-data/chronofact.sqlite3" ^
  --case-id "CASE-001" ^
  --examiner "examiner1" ^
  --title "Digital Forensic Case Report" ^
  --output-root "./reports"
```

### Generate with Findings
Create `findings.json`:
```json
{
  "case_id": "CASE-001",
  "findings": [
    {
      "id": "F-001",
      "title": "Unauthorized file transfer",
      "classification": "observation",
      "review_status": "reviewed",
      "reviewer": "examiner1",
      "description": "Large file downloaded at off-hours",
      "benign_explanations": ["Could be scheduled backup task"],
      "sources": [
        {
          "evidence_id": "EV-9F51C8",
          "source_locator": "csv_line=12",
          "anchor_text": "File transfer logged at 2025-09-12T23:45:00Z"
        }
      ]
    }
  ]
}
```

Generate report:
```powershell
python phase5_report.py ^
  --db "./chronofact-data/chronofact.sqlite3" ^
  --case-id "CASE-001" ^
  --examiner "examiner1" ^
  --findings-json "./findings.json" ^
  --output-root "./reports"
```

### Include Analysis Results
```powershell
python phase5_report.py ^
  --db "./chronofact-data/chronofact.sqlite3" ^
  --case-id "CASE-001" ^
  --examiner "examiner1" ^
  --disk-manifest "./disk-output/manifest.json" ^
  --memory-manifest "./memory-output/manifest.json" ^
  --output-root "./reports"
```

### Outputs
- `reports/report-*/case_report.pdf` - Court-ready PDF
- `reports/report-*/case_report.docx` - Editable Word document
- `reports/report-*/case_report.html` - Web report
- `reports/report-*/case_report.json` - Machine-readable
- `reports/report-*/evidence.csv` - Evidence inventory
- `reports/report-*/output_manifest.json` - Output checksums

---

## ML Training (Phase 6)

### Requirements
- **Labeled training CSV** (you must manually review and label events)
- At least 4 distinct scenarios/groups
- Label must be 0 or 1 only
- Timestamp must include timezone

### Training CSV Schema
```csv
event_id,scenario_id,timestamp,source,action,bytes,label
E001,SYNTH-A,2026-10-01T09:00:00Z,logon,login,0,0
E002,SYNTH-A,2026-10-01T09:05:00Z,file,download,2048,0
E003,SYNTH-B,2026-10-02T21:00:00Z,http,upload,9500000,1
E004,SYNTH-B,2026-10-02T21:05:00Z,http,upload,9200000,1
```

### Train Model
```powershell
python phase6_ml.py train ^
  --input "./training.csv" ^
  --output-root "./model-runs" ^
  --group-column "scenario_id" ^
  --label-column "label" ^
  --positive-label-definition "Adjudicated data exfiltration events"
```

**Outputs:**
- `model-runs/train-*/model.joblib` - Trained model
- `model-runs/train-*/metrics.json` - Evaluation metrics
- `model-runs/train-*/holdout_predictions.csv` - Test results
- `model-runs/train-*/model_metadata.json` - Model metadata

### Score New Data
```powershell
python phase6_ml.py score ^
  --model "./model-runs/train-*/model.joblib" ^
  --input "./new_events.csv" ^
  --output-root "./score-runs"
```

### Important Notes
- **Not calibrated probabilities**: Scores are not guilt probabilities
- **Grouped holdout**: Ensures scenarios don't leak into training/test
- **Requires validation**: Must be validated with agency data before operational use
- **Label=1**: Must mean "confirmed target" (not "unknown")
- **Label=0**: Must mean "confirmed benign" (not "unknown")

---

**Version**: 2.0.0 | **Date**: 2026-10-11
