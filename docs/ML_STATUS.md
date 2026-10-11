# CHRONOFACT Phase 6 ML Model Status

## ✅ Model Trained

**Training Run:** `train-20261011-120155-f690b5c5`  
**Date:** 2026-10-11  
**Model File:** `model.joblib` (328KB)

---

## Training Data

| Metric | Value |
|--------|-------|
| Total Events | 100 |
| Training Scenarios | 3 (65 events) |
| Test Scenarios | 2 (35 events) |
| Groups Disjoint | ✅ Yes |

**Dataset:** `training_data.csv`  
- **SCENARIO_A, SCENARIO_C, SCENARIO_E:** Benign (label=0)  
- **SCENARIO_B, SCENARIO_D:** Malicious (label=1)

---

## Evaluation Metrics (Holdout)

| Metric | Score |
|--------|-------|
| Precision | 1.0000 |
| Recall | 1.0000 |
| F1-Score | 1.0000 |
| Average Precision | 1.0000 |
| ROC-AUC | 1.0000 |

**Confusion Matrix:**
```
Predicted 0  Predicted 1
Actual 0    10           0
Actual 1     0          25
```

---

## Using the Trained Model

### Score New Events

```powershell
cd C:\Users\antriksh\Downloads\arpit_hackathon\chronofact_installed\chronofact
python phase6_ml.py score `
  --model ./model-runs/train-20261011-120155-f690b5c5/model.joblib `
  --input ./new_events.csv `
  --output-root ./score-runs
```

### Files Generated
- `model.joblib` - Trained Random Forest model
- `metrics.json` - Full evaluation report
- `model_metadata.json` - Training run metadata
- `holdout_predictions.csv` - Test results

---

## Important Notes

⚠️ **These are synthetic data results.** The model needs validation on agency-authorized real data before operational use.

⚠️ **Score is NOT a probability of guilt.** It flags statistical anomalies for examiner review.

---

## Status

✅ **All Phases 0-6 Complete:**
| Phase | Status |
|-------|--------|
| 0-2 (API/Security) | ✅ Running |
| 3 (Disk) | ✅ Sleuth Kit integrated |
| 4 (Memory) | ✅ Volatility 3 integrated |
| 5 (Reports) | ✅ Tested |
| 6 (ML) | ✅ Model trained |

---

**Date:** 2026-10-11
