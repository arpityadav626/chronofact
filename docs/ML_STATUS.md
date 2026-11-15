# CHRONOFACT Phase 6 ML Model Status

## ✅ Model Trained (Enterprise Benchmark v2)

**Training Run:** `train-20261115-151637-0eb855e7`  
**Algorithm:** `HistGradientBoostingClassifier` (with IST temporal features & burst dynamics)  
**Date:** 2026-11-15  
**Model File:** `model.joblib` (67KB)

---

## 📊 Training Data (Realistic Enterprise Benchmark v2)

| Metric | Value |
|--------|-------|
| Total Events | 837 |
| Enterprise Scenarios | 52 distinct operational scenarios |
| Training Set | 638 events across 39 scenarios |
| Test Holdout Set | 199 events across 13 completely disjoint scenarios |
| Groups Disjoint | ✅ Yes (Zero scenario leakage) |
| Benign Class (0) | 683 events (81.6%) |
| Malicious Class (1) | 154 events (18.4%) |

**Dataset Features:** `training_data.csv`
- **Shared Action Vocabulary:** Both benign and malicious classes share `upload`, `download`, `login`, `view`, `edit`, and `email_send`.
- **Shared Source Channels:** Both classes share `http`, `smtp`, `sharepoint`, `logon`, `file`, and `terminal`.
- **Realistic Overlap & Noise:** 
  - Scheduled large database backups (18MB - 85MB at 02:00 IST) and late-night crunch work are labeled as **Benign (0)**.
  - Low-volume slow-drip leaks (18KB - 85KB) and daytime exfiltration bursts are labeled as **Malicious (1)**.

---

## 🔬 Benchmark Comparison: Naive Rule vs. Multimodal ML

Evaluated using **Leave-One-Scenario-Out Cross-Validation (52 Groups)**:

| Approach / Model | PR-AUC | Precision @ 0.5 | Recall @ 0.5 | F1-Score | Judicial / Forensic Verdict |
|---|---|---|---|---|---|
| **Naive Heuristic Rule (`bytes > 100k`)** | — | **0.157** | **0.494** | **0.238** | **Fails**: High false-alarm rate (flags DB backups) and misses stealth exfiltration. |
| **Logistic Regression (Balanced)** | 0.995 | 0.967 | 0.948 | 0.957 | Linear baseline capturing IST off-hours and burst speed. |
| **HistGradientBoostingClassifier (Active)** | **0.998** | **0.993** | **0.981** | **0.987** | **Best**: Captures non-linear burst/off-hours interactions with 67KB footprint. |

---

## 🛠️ Feature Engineering Pipeline

The model extracts 10 multi-dimensional forensic signals:
1. `bytes` - Raw byte payload size
2. `log_bytes` - $\ln(1 + \text{bytes})$ scale compression
3. `hour_ist` - Local Indian Standard Time (UTC+05:30)
4. `after_hours` - Off-hours indicator (22:00 - 06:00 IST)
5. `gap_min` - Elapsed minutes since prior event in scenario
6. `burst_score` - $\frac{1}{\text{gap\_min} + 0.1}$ velocity score
7. `day_of_week` - Day of week (0=Monday, 6=Sunday)
8. `source` - One-hot encoded log channel
9. `action` - One-hot encoded operation
10. `user_id` - User entity baseline identifier

---

## 🚀 Running Training and Evaluation

### Train Model:
```powershell
python phase6_ml.py train `
  --input training_data.csv `
  --output-root ./model-runs `
  --model-type hist_gb `
  --positive-label-definition "Malicious exfiltration or reconnaissance log event"
```

### Run Cross-Scenario Group Evaluation:
```powershell
python eval_ml.py training_data.csv
```

### Score New Events:
```powershell
python phase6_ml.py score `
  --model ./model-runs/train-20261115-151637-0eb855e7/model.joblib `
  --input ./new_events.csv `
  --output-root ./score-runs
```

---

## ⚖️ Judicial & Legal Boundaries (BSA 2023 §63(4))

⚠️ **ML is NOT Judicial Proof:**
- Anomaly scores are investigative triage indicators, not evidence of guilt.
- Legal proof of tampering or timestamp discrepancy rests strictly on ChronoFact's **Deterministic Engines**:
  1. Cryptographic dual hashing (SHA-256 + SHA3-256)
  2. Lexicographical Merkle Trees
  3. Allen's Interval Algebra timeline validation
  4. 100% mechanical byte-citation grounding gate
