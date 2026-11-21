# ⚖️ CHRONOFACT 2.0 — National Judicial Cyber Forensic Intelligence Workbench

> **Verifiable, Uncertainty-Aware Digital Evidence Reasoning & Statutory Admissibility Engine**  
> **Compliant with Section 63(4) of Bharatiya Sakshya Adhiniyam, 2023 (BSA)**  
> 
> **SUTRAM 2026 — Round 2 Submission**  
> **Organized by:** Information Security Education and Awareness (ISEA) Project | Ministry of Electronics and Information Technology (MeitY), Government of India  
> **Host Institution:** Department of Information Technology, Indira Gandhi Delhi Technical University for Women (IGDTUW)  
> **Project Lead:** Arpit Yadav & Team  

---

## 📌 Executive Summary

Modern criminal and corporate fraud investigations in India face an acute evidentiary crisis. With the enactment of the **Bharatiya Sakshya Adhiniyam, 2023 (BSA)** replacing the colonial Indian Evidence Act of 1872, digital records are now governed by rigorous statutory standards under **Section 63(4)**. In court trials, standard forensic software and conventional Large Language Models suffer from catastrophic flaws:
1. **Timestamp Hallucination:** Chronological flattening ignores network clock drifts, time-zone offsets, and partial event orderings.
2. **Fabricated Citations:** Generic generative AI invents corroborating quotes and misattributes exhibit numbers, leading to immediate judicial dismissal.
3. **Confirmation Bias:** Triage tools surface only incriminating correlations without proposing mandatory alternative benign hypotheses.
4. **Fragile Custody Chains:** Electronic exhibits lack concurrent cryptographic multi-algorithm hashing and tamper-evident Merkle tree proofs.

**CHRONOFACT 2.0** is a prototype forensic intelligence workbench that runs fully locally built specifically for Cyber Crime Units, State Forensic Science Laboratories (FSLs), and Judicial Magistrates. It fuses **NIST dual-algorithm cryptographic hashing**, **Allen's Interval Temporal Algebra**, **deterministic velocity impossibility analysis**, **mechanical byte-span citation verification**, and **one-click BSA 2023 §63(4) statutory certificate generation**.

---

## 🏛️ Legal & Statutory Framework (BSA 2023 §63(4))

Under **Section 63(4) of the Bharatiya Sakshya Adhiniyam, 2023**, any electronic record submitted as primary or secondary evidence in an Indian court of law must be accompanied by a certificate signed by:
- **Part A:** The person occupying an official position in relation to the operation of the relevant device or the management of the relevant activities (Lawful Custodian).
- **Part B:** An authorized technical forensic expert or cyber examiner confirming the cryptographic hash, device integrity, and uncorrupted transmission.

ChronoFact automates this statutory mandate by maintaining an immutable, dual-algorithm evidence ledger and generating UNSIGNED DRAFT §63(4) certificates that a human officer and expert must review and sign.

---

## ⚡ Key Innovations & Technical Architecture

```
[MULTI-STREAM EVIDENCE INGESTION]
  │  (Server Access CSVs, WhatsApp Exports, RFC-822 EMLs, CDR Tower Logs)
  ▼
[NIST FIPS DUAL-HASH ENGINE & AIR-GAPPED VAULT]
  │  ├── FIPS 180-4 SHA-256 + FIPS 202 SHA3-256 Concurrent Streams (64KB Chunks)
  │  ├── Lexicographical Binary Merkle Tree with Cryptographic Inclusion Proofs
  │  └── 1-Bit Tamper Interceptor -> Raises ForensicIntegrityViolationError
  ▼
[UNCERTAINTY-AWARE HYPER-TIMELINE]
  │  ├── Allen's 13 Temporal Interval Relations ([t_min, t_max] Windows)
  │  └── Dual UTC / IST Timezone Normalization with Clock Drift Tolerance
  ▼
[SPATIO-TEMPORAL INCONSISTENCY RADAR & ML ANOMALY ENGINE]
  │  ├── Haversine Distance & Velocity Impossibility (>800 km/h implied-speed flag)
  │  ├── Unsupervised IsolationForest Telemetry Scoring with Factor Attribution
  │  └── Mandatory 4 Benign Alternative Hypotheses (Bias Prevention Engine)
  ▼
[MECHANICAL CITATION GATE (verbatim byte-span check)]
  │  ├── Verbatim Byte-Span Verification: [byte_start, byte_end] & File Line Anchors
  │  └── Trap Gate: Unsubstantiated / Fabricated Quotes Struck Down with 0.0% Score
  ▼
[JUDICIAL COMPLIANCE & DOSSIER EXPORT]
     ├── BSA 2023 Section 63(4) Part A & Part B Court Affidavits
     ├── RFC-4180 CSV Evidence Manifest with SHA-256 / SHA3-256 Digests
     └── Tamper-Sealed Court ZIP Dossier
```

### 1. Dual-Algorithm Cryptographic Sealing & Merkle Proofs
- Computes concurrent **NIST SHA-256 (FIPS 180-4)** and **SHA3-256 (FIPS 202)** digests using non-allocating 64KB streaming buffers.
- Preserves physical filesystem access timestamps (`atime`) during examination to satisfy strict chain-of-custody protocols.
- Constructs a deterministic, order-invariant **Lexicographical Binary Merkle Tree** generating individual inclusion proofs for every ingested exhibit.
- Employs an uncatchable `ForensicIntegrityViolationError` (inheriting directly from `BaseException`) that bypasses generic `except Exception:` blocks if a single bit of tampering is detected.

### 2. Uncertainty-Aware Hyper-Timeline (Allen's Interval Algebra)
- Discards naive single-point timestamps in favor of bounded intervals $[t_{\min}, t_{\max}]$.
- Implements James Allen's 13 formal interval logic relations (*Precedes*, *Meets*, *Overlaps*, *During*, *Finishes*, etc.).
- Flags partial orderings and marks clock-skewed events as *"Order Undetermined (?)"* rather than presenting misleading chronological certainty to judges.

### 3. Spatio-Temporal Inconsistency Radar (Alibi Buster)
- Correlates multi-source evidence (e.g. mobile chat alibis vs. cellular tower CDR azimuths vs. VPN server logins).
- Calculates geodesic Haversine distance and flags kinematic velocity impossibilities (e.g., physical travel exceeding commercial vehicle limits between successive timestamped actions).
- **Anti-Confirmation Bias Gate:** Generates 4 mathematically plausible benign explanations (e.g., automated batch script execution, VPN proxy routing, shared family device, carrier NAT translation) for every flagged anomaly.

### 4. Mechanical Citation Verifier (Zero-Hallucination Gate)
- Every finding, entity, and summary generated by the system is mechanically verified against original source bytes.
- Anchors quotes with exact `(byte_start, byte_end)` byte spans and line numbers.
- If an assertion cannot be found verbatim in the seized evidence, it is struck through in red and assigned a strict **0.0% Grounding Score**.

### 5. Unsupervised Machine Learning Anomaly Detection
- Integrates an **IsolationForest** model trained on high-dimensional forensic log telemetry.
- Evaluates operation criticality weights, off-hours execution windows (22:00–06:00), action burst intervals, and external CIDR address classifications.
- Provides transparent, human-interpretable factor attribution rather than opaque black-box scores.

---

## 📂 Repository Directory Structure

```text
chronofact/
├── app/
│   ├── core/
│   │   ├── auth.py                 # JWT authentication, bcrypt hashing, RBAC
│   │   ├── config.py               # Application paths, vault directory, environment
│   │   ├── crypto.py               # SHA-256 digest computation & hash-chained audit log
│   │   ├── database.py             # SQLite schema, indices & FTS5 full-text engine
│   │   ├── forensic_hasher.py      # Dual-hash engine, Merkle trees & tamper detector
│   │   ├── security.py             # HTTP security headers, CSP, rate limiting
│   │   └── vault.py                # AES-256-GCM encrypted evidence vault storage
│   ├── engines/
│   │   ├── entity_extractor.py     # Regex & deterministic NER (IPs, emails, phones)
│   │   ├── inconsistency.py        # Haversine alibi conflict & benign hypothesis generator
│   │   ├── ml_anomaly.py           # IsolationForest log anomaly scoring & factor weights
│   │   ├── ml_engine.py            # Hybrid semantic RAG & TF-IDF exhibit retriever
│   │   ├── ml_model.py             # Serialization & inference pipeline for anomaly models
│   │   ├── rag_engine.py           # Multi-document retrieval with strict provenance
│   │   ├── timeline_engine.py      # Allen's interval algebra & dual-clock normalization
│   │   ├── training_pipeline.py    # Grouped-holdout ML training & validation workflow
│   │   └── verifier.py             # Mechanical byte-span verifier & grounding gate
│   ├── legal/
│   │   └── bsa_certificate.py      # BSA 2023 §63(4) Part A & Part B court certificate generator
│   ├── parsers/
│   │   ├── chat_parser.py          # WhatsApp, Telegram & text chat export parser
│   │   ├── csv_log_parser.py       # Server auth, access, firewall & CDR CSV parser
│   │   └── email_parser.py         # RFC 822 .eml MIME parser with transmission hop analysis
│   ├── static/
│   │   ├── app.js                  # Frontend interactive forensic workbench controller
│   │   ├── index.html              # Dark obsidian cyber forensic workbench UI
│   │   ├── login.html              # Secure examiner login interface
│   │   └── styles.css              # Cyber forensic UI design system & responsive styling
│   └── main.py                     # FastAPI core backend application & REST endpoints
├── docs/                           # Comprehensive technical, operational & security manuals
│   ├── INDEX.md                    # Documentation index & architecture overview
│   ├── ML_STATUS.md                # Machine learning validation & benchmark status
│   ├── OPERATIONAL.md              # Standard Operating Procedures (SOP) for examiners
│   ├── SECURITY.md                 # Threat model, air-gap guidelines & encryption specs
│   ├── SETUP.md                    # Detailed environment setup & troubleshooting
│   ├── TROUBLESHOOTING.md          # Diagnostic runbook for common edge cases
│   └── USAGE.md                    # Complete examiner workflow walkthrough
├── sample_evidence/                # Pre-packaged synthetic corporate espionage case
│   ├── server_access.csv       # Server authentication timestamps & external IP logs
│   ├── whatsapp_chat.txt      # Suspect's WhatsApp claims & conflicting statements
│   ├── telecom_cdr_tower.csv       # Cell tower azimuth, sector ID & coordinates
│   └── confidential_leak.eml # RFC 822 exfiltration email with MIME attachments
├── tests/                          # automated test suite
│   ├── test_backend_accuracy_engines.py # Allen's algebra, alibi radar & citation gates
│   ├── test_forensic_integrity.py       # NIST test vectors, Merkle proofs & 1-bit tampering
│   ├── test_ml_models.py                # IsolationForest anomaly scoring & RAG verification
│   └── test_new_ml_model.py             # Edge-case feature extraction & inference tests
├── .env.example                    # Template for environment configuration
├── Dockerfile                      # Containerization recipe for reproducible deployments
├── docker-compose.yml              # Local container orchestration
├── requirements.txt                # Production Python dependencies
├── run.py                          # 1-click cross-platform Python server launcher
├── start.bat                       # 1-click Windows native launch script
└── START_FULL.bat                  # Full environment launcher with production defaults
```

---

## 🚀 Quick Start & Installation

### System Prerequisites
- **Operating System:** Windows 10/11, Ubuntu 20.04+, macOS 12+
- **Python:** Python 3.10, 3.11, or 3.12
- **Memory:** 4 GB RAM minimum (8 GB recommended)
- **Disk:** 500 MB free space (plus evidence storage)

---

### Step 1: Clone or Extract the Project

```bash
# Navigate to the project root directory
cd chronofact
```

---

### Step 2: Set Up Python Virtual Environment

#### On Windows (PowerShell / Command Prompt):
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

#### On Linux / macOS:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

### Step 3: Run CHRONOFACT

#### Option A: Quick 1-Click Launch (Windows)
Double-click `start.bat` or run:
```cmd
start.bat
```

#### Option B: Cross-Platform Python Launch
```bash
python run.py
```

The interactive workbench will start immediately:
```text
============================================================
Starting CHRONOFACT — Digital Forensic Investigation Workbench
Serving interactive UI at: http://127.0.0.1:8000
============================================================
```

Open your browser and navigate to: **`http://127.0.0.1:8000`**

---

### Step 4: Login Credentials

ChronoFact includes role-based authentication for forensic examiners:
- **Default Username:** `examiner`
- **Default Password:** `SecurePassMin16Chars!`

*(Credentials and secrets can be customized in `.env` or system environment variables).*

---

## 🔍 Guided Demonstration Walkthrough (Sample Case)

ChronoFact comes pre-loaded with a complete, synthetic corporate insider threat investigation (**Operation Apex Exfiltration / Vikram Malhotra Case**).

### 1. Ingest Case Exhibits
1. Click **"⚡ Load Sample Case Exhibit"** in the top navigation bar.
2. The system instantaneously ingests four disparate evidence streams:
   - `server_access.csv`: Production server authentication and SCP file transfer records.
   - `whatsapp_chat.txt`: Suspect's WhatsApp claims insisting he was asleep at home.
   - `telecom_cdr_tower.csv`: Telecom antenna coordinates and azimuth connections.
   - `confidential_leak.eml`: Exfiltrated project source code with RFC-822 email headers.

### 2. Inspect Cryptographic Sealing & Merkle Tree
- Navigate to the **Evidence Vault** tab.
- Observe each file's dual NIST SHA-256 and SHA3-256 cryptographic hashes calculated over 64KB streaming buffers.
- Click **"Audit Merkle Tree"** to view the master root digest and inspect the individual cryptographic inclusion proof paths.

### 3. Explore the Hyper-Timeline
- View the unified interactive timeline normalized across UTC and Indian Standard Time (IST).
- Notice how events are bounded with $[t_{\min}, t_{\max}]$ confidence intervals, exposing subtle transmission delays between email header hops and server commits.

### 4. Trigger the Inconsistency Radar (Alibi Buster)
- Scroll to the **Inconsistency Radar** card.
- **The Finding:** Suspect claims in WhatsApp at `15:25 IST` that he is sleeping at his residence in Noida Sector 62. However, cellular CDR logs record his phone connecting to Tower `DEL-S-041` in Okhla Phase III at `15:27 IST` (+24.8 km distance), followed by authenticated server access logs downloading confidential financial models at `15:28 IST`.
- **Physical Velocity Check:** Moving 24.8 km in ~92 seconds requires an impossible velocity of **970.0 km/h** (and over 490 km/h even across 3 minutes), physically impossible by ground transit.
- **Benign Counter-Hypotheses:** ChronoFact automatically presents 4 alternative explanations (e.g. tower signal bounce, SIM clone, forwarded call, carrier network realignment) to ensure impartial judicial reporting.

### 5. Generate BSA 2023 Section 63(4) Legal Certificate
1. Click **"Generate Legal Certificate (BSA §63(4))"**.
2. Fill in the Court Name (*Chief Metropolitan Magistrate, New Delhi*) and FIR / Case Number (*FIR No. 402/2026*).
3. Click **"Generate Statutory Certificate"**.
4. The system produces:
   - **Part A:** Certificate by Lawful Custodian.
   - **Part B:** Certificate by Technical Forensic Examiner.
   - Complete Hash Disclosure Schedule listing SHA-256, SHA3-256, byte sizes, and Merkle root.
   - Export options for printable HTML, RFC-4180 CSV manifest, and a tamper-sealed ZIP dossier.

---

## 🧪 Automated Forensic Accuracy Test Suite

To verify that the cryptographic, algorithmic, and legal engines operate as covered by the test suite, run the automated test suite:

### Test 1: Cryptographic Integrity & NIST Test Vectors
Validates NIST FIPS 180-4 and FIPS 202 digests against official NIST test vectors, streaming chunk equivalence, `atime` preservation, Merkle inclusion proofs, and 1-bit tamper interception:
```bash
python tests/test_forensic_integrity.py
```
*Expected Output:* `ALL 6 FORENSIC INTEGRITY & CRYPTOGRAPHIC TESTS PASSED`

### Test 2: Backend Accuracy Engines (Allen's Algebra & Citation Gate)
Validates interval temporal algebra, Haversine velocity calculations, mechanical byte-span citation grounding, and statutory certificate generation:
```bash
python tests/test_backend_accuracy_engines.py
```
*Expected Output:* `ALL 4 BACKEND ACCURACY ENGINES PASSED ZERO-HALLUCINATION VERIFICATION`

### Test 3: Machine Learning Anomaly Detection & Factor Weights
Validates IsolationForest telemetry scoring, RAG semantic search grounding, and dynamic multi-log feature extraction:
```bash
python tests/test_ml_models.py
```
*Expected Output:* `ALL MACHINE LEARNING ACCURACY TESTS PASSED`

---

## 🛡️ Security, Privacy & Air-Gap Compliance

- **Zero Cloud Dependence:** All natural language extraction, cryptographic hashing, and interval calculations run entirely on the local host. No evidence ever leaves the examination machine.
- **Read-Only Ingestion:** Evidence files are opened strictly in read-only binary mode (`rb`), guaranteeing that access timestamps (`atime`) and modified timestamps (`mtime`) remain unchanged on physical media.
- **Evidence Vault Security:** Seized exhibits are stored in a dedicated containment vault with strict path-confinement and sanitize guards. An optional AES-256-GCM encrypted-at-rest mode (`CHRONOFACT_VAULT_KEY_B64`) is available for untrusted storage environments, while default forensic mode maintains bitstream byte-identity for direct FSL hexadecimal audits.
- **Enterprise Defense in Depth:** Includes Content Security Policy (CSP) headers, HTTP Strict Transport Security (HSTS), XSS protection, anti-clickjacking frame guards, and cryptographic session rate limiting.

---

## 👥 Team & Submission Information

- **Event:** SUTRAM 2026 — Round 2 Evaluation
- **Theme:** Cyber Forensics, Digital Evidence Admissibility & Information Security
- **Under the Auspices of:** Information Security Education and Awareness (ISEA) Project | Ministry of Electronics and Information Technology (MeitY)
- **Host Department:** Department of Information Technology, IGDTUW, Delhi
- **Lead Developer & System Architect:** Arpit Yadav
- **Repository / Live Demonstration:** [https://arpityadav626.github.io/chronofact/](https://arpityadav626.github.io/chronofact/)
- **Video Walkthrough Demonstration:** [https://youtu.be/J8VqyTlGd5w](https://youtu.be/J8VqyTlGd5w)

---

## 📜 License

This project is licensed under the **Apache License 2.0**. See the [LICENSE](LICENSE) file for complete terms. Developed for academic evaluation, law enforcement research, and judicial evidence modernization.


---

## Security & honesty notes (v2)

- **Run it:** `pip install -r requirements.txt`, copy `.env.example` to `.env`, set `CHRONOFACT_USER`/`CHRONOFACT_PASSWORD` and `JWT_SECRET_KEY`, then `python run.py`. For a public demo set `CHRONOFACT_DEMO_MODE=true` (accounts `examiner` / `analyst`, never in production).
- All `/api/*` routes need a bearer token; there are no built-in passwords. Failed logins lock a client+user pair for 5 minutes.
- Merkle scheme is `RFC6962-style/SHA-256/v2` (0x00 leaf / 0x01 node prefixes, odd nodes promoted). Roots from older builds differ by design.
- The audit log is append-only (DB triggers) and `GET /api/audit/verify` recomputes the whole chain. It is tamper-*evident*, not tamper-proof: anchor the head hash externally (signed, printed or timestamped) for real assurance.
- **Citation gate:** answers are extractive (verbatim excerpts), so "no fabricated quotes" holds by construction. It does not make the *interpretation* correct.
- **ML is a triage aid.** Metrics come from a synthetic dataset (perfect holdout scores indicate the generator is easy, not real-world accuracy). IsolationForest flags a fixed fraction of any data.
- **Not air-gapped as shipped:** the pages load Tailwind, Lucide and Google Fonts from CDNs. Vendor them locally (and pin versions) before claiming offline operation.
- **Legal:** the certificate is a draft. Admissibility is decided by the court; this tool is not legal advice and is not a FIPS-validated module (it uses standard SHA-256/SHA3-256 algorithms through Python/OpenSSL).
- Chat exports have no UTC offset; correlation rules assume `CHRONOFACT_ASSUMED_CHAT_TZ` (default +05:30) and disclose that in each finding.
