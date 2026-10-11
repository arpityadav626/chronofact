# CHRONOFACT Documentation Index

## Overview
**Project Location**: `C:\Users\antriksh\Downloads\arpit_hackathon\chronofact_installed\chronofact`

**Version**: 2.0.0 (Phases 0-6 Integrated)

**Date**: 2026-10-11

---

## Documentation Files

| Document | Purpose | Links |
|----------|---------|-------|
| **README.md** | Project overview, quick start | [docs/README.md](README.md) |
| **SETUP.md** | Installation and configuration | [docs/SETUP.md](SETUP.md) |
| **USAGE.md** | Detailed usage examples | [docs/USAGE.md](USAGE.md) |
| **SECURITY.md** | Security architecture and key management | [docs/SECURITY.md](SECURITY.md) |
| **OPERATIONAL.md** | Real-life deployment checklist | [docs/OPERATIONAL.md](OPERATIONAL.md) |
| **TROUBLESHOOTING.md** | Error messages and solutions | [docs/TROUBLESHOOTING.md](TROUBLESHOOTING.md) |

---

## Quick Access

### Getting Started
1. Read **SETUP.md** - Installation instructions
2. Start server: `START_FULL.bat`
3. Test: `curl http://127.0.0.1:8007/`

### Using Features
- **Upload evidence**: See USAGE.md - API Usage
- **Disk analysis**: See USAGE.md - Disk Analysis
- **Memory analysis**: See USAGE.md - Memory Analysis
- **Generate reports**: See USAGE.md - Report Generation
- **Train ML model**: See USAGE.md - ML Training

### Security & Operations
- **Vault key management**: See SECURITY.md - Key Management
- **Deployment checklist**: See OPERATIONAL.md - Deployment Checklist
- **Real-life requirements**: See OPERATIONAL.md - Real-Life Deployment Checklist

### Troubleshooting
- **Error messages**: See TROUBLESHOOTING.md
- **Verification commands**: See TROUBLESHOOTING.md - Verification Commands

---

## Project Structure

```
chronofact/
├── app/
│   ├── main.py          # Secure API (Phases 0-2)
│   └── core/
│       ├── auth.py      # Operator authentication
│       ├── config.py    # Configuration
│       └── vault.py     # AES-GCM encryption
├── phase3_disk.py       # Disk analysis (Phase 3)
├── phase4_memory.py     # Memory analysis (Phase 4)
├── phase5_report.py     # Report generation (Phase 5)
├── phase6_ml.py         # ML training (Phase 6)
├── chronofact-data/     # SQLite + vault
├── docs/                # This documentation
├── .env                 # Environment (DO NOT COMMIT)
├── README.md            # Project overview
├── START.bat            # Basic start
└── START_FULL.bat       # Full start with tools
```

---

## External Tools Status

| Tool | Version | Status | Location |
|------|---------|--------|----------|
| Sleuth Kit | 4.14.0 | ✅ Installed | `C:\Users\antriksh\Downloads\sleuthkit-4.14.0-win32\sleuthkit-4.14.0-win32\bin` |
| Volatility 3 | 2.28.2 | ✅ Installed | `C:\Users\antriksh\Downloads\volatility3` |

---

## Important Notes

**Security:**
- Never commit `.env` to Git
- Back up vault key separately from database
- Run on isolated forensic workstation

**Legal:**
- Agency review required before operational use
- ML models require independent validation
- This system does NOT generate BSA §63(4) certificates

**Operational:**
- Hardware write-blockers required for acquisition
- Examiner review required for all findings
- Documentation of acquisition process required

---

**Questions?** See TROUBLESHOOTING.md for common issues.
