# CHRONOFACT — Digital Forensic Investigation Workbench

> **Verifiable, Uncertainty-Aware Evidence Reasoning with BSA 2023 Section 63(4) Legal Compliance**

CHRONOFACT is a local, privacy-first digital forensic triage system designed for law enforcement (Cyber Crime Units, FSLs) and corporate forensic teams.

---

## 🚀 Key Features

1. **Cryptographic Chain of Custody:**
   - Automatic NIST SHA-256 hash calculation upon evidence upload.
   - Hash-chained, tamper-evident audit log ensuring legal traceability.
2. **Uncertainty-Aware Hyper-Timeline:**
   - Replaces flat chronological timelines with intervals $[t_{\min}, t_{\max}]$.
   - Identifies partial ordering and flags ambiguous time zones with "Order Undetermined (?)".
3. **Deterministic Inconsistency Radar:**
   - Detects alibi contradictions (e.g. suspect claiming to be asleep on chat vs active server login).
   - Surfaces document modification vs transmission delays.
   - Attaches mandatory **benign explanations** to prevent confirmation bias.
4. **Mechanical Citation Verifier (0% Hallucination Gate):**
   - AI answers are intercepted by a deterministic AST & byte-span verifier.
   - Quotes that do not exist verbatim in original evidence are struck through in red.
5. **Indian Court Compliance (BSA 2023 s.63(4)):**
   - Generates 1-click compliant Part A (Custodian) and Part B (Examiner) certificates with complete hash disclosure schedules.

---

## 📂 Project Structure

```text
chronofact/
├── app/
│   ├── core/
│   │   ├── config.py           # Paths, vault location, constants
│   │   ├── crypto.py           # SHA-256 hashing & hash-chained audit log
│   │   └── database.py         # SQLite schema & FTS5 full-text search
│   ├── parsers/
│   │   ├── email_parser.py     # RFC 822 .eml parser with hop headers
│   │   ├── chat_parser.py      # WhatsApp / text chat export parser with timezone intervals
│   │   └── csv_log_parser.py   # Server authentication & access logs
│   ├── engines/
│   │   ├── timeline_engine.py  # Interval-based partial order timeline
│   │   ├── inconsistency.py    # Deterministic conflict detection rules
│   │   └── verifier.py         # Mechanical byte-span citation verifier
│   ├── legal/
│   │   └── bsa_certificate.py  # Bharatiya Sakshya Adhiniyam s.63(4) certificate generator
│   ├── static/
│   │   ├── index.html          # Interactive forensic workbench dashboard
│   │   ├── styles.css          # Dark forensic UI stylesheet
│   │   └── app.js              # Frontend REST controller
│   └── main.py                 # FastAPI application
├── sample_evidence/            # Pre-packaged data leak case for testing
├── data/                       # Local SQLite DB and immutable vault (auto-created)
├── requirements.txt
├── run.py                      # 1-click startup script
└── README.md
```

---

## ⚡ Quick Start

```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run CHRONOFACT
python run.py
```

Open your browser at: **`http://127.0.0.1:8000`**

Click **"⚡ Load Sample Case Exhibit"** to immediately test the system with pre-built corporate fraud evidence!
