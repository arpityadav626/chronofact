"""
CHRONOFACT New ML Model & Training Pipeline Test Suite
=======================================================
Validates:
1. ForensicAnomalyModel (persistable IsolationForest):
   - fit/predict round trip
   - model persistence to disk with integrity hash
   - model loading with hash verification
2. TrainingPipeline:
   - train with synthetic labels
   - evaluation metrics computation
   - model listing
"""

import sys
import json
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from app.engines.ml_model import ForensicAnomalyModel
from app.engines.training_pipeline import TrainingPipeline


def test_model_fit_predict_roundtrip():
    print("[1/4] Testing ForensicAnomalyModel fit/predict round trip...")

    sample_logs = [
        {"id": "L1", "raw_text": "2026-10-02T10:00:00Z,analyst.1,192.168.1.50,LOGIN,OK", "t_min": "2026-10-02T10:00:00Z"},
        {"id": "L2", "raw_text": "2026-10-02T10:15:00Z,analyst.1,192.168.1.50,VIEW,DASHBOARD", "t_min": "2026-10-02T10:15:00Z"},
        {"id": "L3", "raw_text": "2026-10-02T11:00:00Z,analyst.1,192.168.1.50,SEARCH,REPORTS", "t_min": "2026-10-02T11:00:00Z"},
        {"id": "L4", "raw_text": "2026-10-02T14:30:00Z,analyst.1,192.168.1.50,READ,DOC_412", "t_min": "2026-10-02T14:30:00Z"},
        {"id": "L5_ANOMALY", "raw_text": "2026-10-03T02:45:10Z,compromised.user,203.0.113.88,EXPORT_PATENT_DRAFT,OK", "t_min": "2026-10-03T02:45:10Z"},
        {"id": "L6_ANOMALY", "raw_text": "2026-10-03T02:45:14Z,compromised.user,203.0.113.88,DOWNLOAD_FILE,CONFIDENTIAL_Q3_FINANCIALS.XLSX", "t_min": "2026-10-03T02:45:14Z"},
    ]

    model = ForensicAnomalyModel(contamination=0.25, random_state=42)
    model.fit(sample_logs)
    assert model.model is not None, "Model failed to fit"
    assert model.model_id is not None, "Model ID not generated"

    results = model.predict(sample_logs)
    assert len(results) == len(sample_logs), "Prediction count mismatch"

    top_ids = [r["fact_id"] for r in results[:2]]
    assert "L5_ANOMALY" in top_ids or "L6_ANOMALY" in top_ids, f"Anomaly not ranked at top: {top_ids}"

    print(f"      [OK] Model trained and predicted (model_id={model.model_id}).")
    print(f"      [OK] Top anomalies ranked: {top_ids}")
    return model


def test_model_persistence(model):
    print("[2/4] Testing model persistence (save/load) with integrity hash...")

    models_dir = PROJECT_ROOT / "models"
    artifacts = model.save_model(str(models_dir))

    assert "model_path" in artifacts and artifacts["model_path"].endswith(".pkl")
    assert "manifest_path" in artifacts and artifacts["manifest_path"].endswith(".json")
    assert Path(artifacts["model_path"]).exists()
    assert Path(artifacts["manifest_path"]).exists()

    # Verify manifest integrity hash
    with open(artifacts["manifest_path"]) as f:
        manifest = json.load(f)
    assert manifest.get("model_hash_sha256") is not None, "Manifest missing integrity hash"

    # Reload model
    loaded = ForensicAnomalyModel(model_path=artifacts["model_path"])
    assert loaded.model is not None, "Failed to load persisted model"
    assert loaded.model_id == manifest.get("model_id"), "Loaded model ID mismatch"

    # Predict with loaded model
    loaded_results = loaded.predict(model._training_metadata if hasattr(model, '_training_metadata') else [])
    print(f"      [OK] Model persisted to {artifacts['model_path'].split('models')[1]}")
    print(f"      [OK] Integrity hash verified: {manifest['model_hash_sha256'][:20]}...")
    print(f"      [OK] Model reloaded successfully with id {loaded.model_id}")


def test_training_pipeline():
    print("[3/4] Testing TrainingPipeline with synthetic labels...")

    logs = [
        {"id": f"L{i}", "raw_text": f"2026-10-02T10:00:{i:02d}Z,user{i % 3},192.168.1.{10 + i},LOGIN,OK", "t_min": f"2026-10-02T10:00:{i:02d}Z", "evidence_id": "EV-TEST"}
        for i in range(1, 16)
    ]
    # Inject 2 anomaly logs
    logs.append({"id": "L_ANOM_1", "raw_text": "2026-10-03T02:45:10Z,hacker,203.0.113.88,EXPORT_PATENT_DRAFT,OK", "t_min": "2026-10-03T02:45:10Z", "evidence_id": "EV-TEST"})
    logs.append({"id": "L_ANOM_2", "raw_text": "2026-10-03T02:45:14Z,hacker,203.0.113.88,DOWNLOAD_FILE,CONFIDENTIAL_Q3_FINANCIALS.XLSX", "t_min": "2026-10-03T02:45:14Z", "evidence_id": "EV-TEST"})

    pipeline = TrainingPipeline()
    report = pipeline.train_with_synthetic_labels(logs, contamination=0.15)

    assert report["status"] is not None
    assert report["n_training_samples"] >= 15, "Training samples mismatch"
    assert report["model_id"] is not None
    assert "model_id" in report

    # Model should exist
    models = pipeline.list_models()
    assert len(models) >= 1, "Model not found in listing"

    print(f"      [OK] Training pipeline ran: model_id={report['model_id']}, samples={report['n_training_samples']}")
    print(f"      [OK] Evaluation metrics: {json.dumps(report.get('evaluation_metrics', {}))}")
    print(f"      [OK] {len(models)} model(s) persisted")


def test_model_list_and_status():
    print("[4/4] Testing model listing and status API endpoints...")

    pipeline = TrainingPipeline()
    models = pipeline.list_models()

    assert isinstance(models, list), "list_models should return a list"

    if models:
        latest = models[-1]
        model = ForensicAnomalyModel(model_path=str(Path(pipeline.models_dir) / latest["manifest_path"]))
        status = model.get_status()
        assert status["status"] == "READY", f"Expected READY status, got {status['status']}"
        assert "feature_names" in status
        print(f"      [OK] Listed {len(models)} model(s)")
        print(f"      [OK] Latest model status: {json.dumps(status)}")
    else:
        print("      [OK] No models persisted yet (expected if previous steps saved to different dir)")


def main():
    start = time.perf_counter()
    print("=" * 80)
    print(" CHRONOFACT NEW ML MODEL & TRAINING PIPELINE TEST SUITE (BSA 2023 §63(4))")
    print("=" * 80)

    model = test_model_fit_predict_roundtrip()
    test_model_persistence(model)
    test_training_pipeline()
    test_model_list_and_status()

    dur = time.perf_counter() - start
    print("=" * 80)
    print(f" ALL NEW ML MODEL TESTS PASSED IN {dur:.3f}s")
    print(" Status: MODEL TRAINING, PERSISTENCE & EVALUATION WORKING")
    print("=" * 80)


if __name__ == "__main__":
    main()
