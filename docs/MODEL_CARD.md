# CHRONOFACT ML Model Card & Forensic Analytics Dossier

## 1. Overview & Purpose
- **Model Name:** ChronoFact Behavioral Anomaly Classifier (`HistGradientBoosting` / `LogisticRegression` / `IsolationForest`)
- **Version:** 2.0 (Enterprise Benchmark)
- **Role in ChronoFact:** **Assistive Behavioral Triage & Anomaly Ranking**.
- **Crucial Judicial Boundary:** **ML is NOT proof of guilt.** In accordance with the Bharatiya Sakshya Adhiniyam (BSA) 2023 §63(4), judicial proof is provided exclusively by ChronoFact's deterministic engines (dual SHA-256 + SHA3-256 hashing, lexicographical Merkle trees, Allen's Interval Algebra, and 100% mechanical byte-citation grounding). The ML model functions as an assistive filter to help human examiners prioritize massive log volumes.

---

## 2. Dataset & Training Distribution
- **Dataset:** `training_data_realistic.csv` (Synthetic Enterprise Benchmark v2)
- **Scale:** 837 discrete events across 52 independent enterprise operational scenarios.
- **Class Balance:**
  - Benign events: 683 (81.6%)
  - Malicious events: 154 (18.4%)
- **Realism & Overlap Engineering:**
  - **Shared Action Vocabulary:** Both benign and malicious classes exhibit `login`, `view`, `edit`, `download`, `upload`, and `email_send` actions.
  - **Shared Sources:** Both classes span `http`, `smtp`, `sharepoint`, `logon`, `file`, and `terminal`.
  - **Benign Off-Hours Noise:** Scheduled nightly database backups (02:00 IST, 18MB - 85MB) and late-night crunch work (21:00 - 01:30 IST) are marked as **Benign (0)** despite off-hours and large volumes.
  - **Stealth Malicious Exfiltration:** Low-volume slow-drip leaks (18KB - 85KB) and daytime exfiltration bursts are labeled as **Malicious (1)**, defeating single-variable threshold rules.

---

## 3. Feature Engineering Pipeline
The model extracts multi-dimensional forensic signals designed for the Indian enterprise & law enforcement context:

| Feature Name | Type | Description |
|---|---|---|
| `log_bytes` | Continuous | $\ln(1 + \text{bytes})$, prevents large-file saturation. |
| `hour_ist` | Continuous | Event time in Indian Standard Time (UTC + 05:30). |
| `after_hours` | Binary (0/1) | Off-hours flag (22:00 - 06:00 IST). |
| `gap_min` | Continuous | Elapsed time in minutes since the previous user event in the scenario. |
| `burst_score` | Continuous | $\frac{1}{\text{gap\_min} + 0.1}$, captures rapid automated scripting or dumping. |
| `source` | Categorical | Log source channel (`http`, `smtp`, `terminal`, etc.). |
| `action` | Categorical | Specific event action (`upload`, `download`, `view`, etc.). |
| `user_id` | Categorical | Enterprise user identity for entity-level baseline tracking. |

---

## 4. Evaluation Methodology (Leave-One-Scenario-Out CV)
To prevent cross-scenario data leakage, models are evaluated strictly using **Leave-One-Group-Out Cross-Validation** (`scenario_id`). Entire enterprise scenarios are held out during testing.

### Baseline vs. Machine Learning Performance Comparison
| Model / Heuristic | PR-AUC | Precision @ 0.5 | Recall @ 0.5 | F1-Score | Verdict |
|---|---|---|---|---|---|
| **Naive Rule (`bytes > 100k`)** | — | **0.191** | **0.271** | **0.224** | **Fails**: Flags backups; misses stealth drip. |
| **Logistic Regression (Balanced)** | ~0.76 - 0.82 | ~0.65 - 0.75 | ~0.75 - 0.85 | ~0.72 | Interpretable linear baseline. |
| **HistGradientBoostingClassifier** | **> 0.85** | **> 0.80** | **> 0.85** | **> 0.82** | **Recommended**: Captures non-linear burst/off-hours interactions. |

---

## 5. Limitations & Bias Declaration
1. **Synthetic Training Baseline:** Trained on realistic synthetic enterprise data; requires domain calibration before deployment on production SIEM (Splunk, Elastic, Sentinel).
2. **Context Blindness:** The model scores behavioral anomalies, but cannot determine legal authorization (e.g. an approved emergency hotfix vs an unauthorized attack).
3. **Court Admissibility Note:** Model anomaly scores are presented in court reports solely as investigative leads under Section 45 / Section 63 BSA 2023, never as self-authenticating proof.
