"""
CHRONOFACT Training Pipeline
============================
Train, evaluate, and deploy forensic anomaly detection models.
Generates evaluation metrics (precision/recall on labeled data).
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split

from .ml_model import ForensicAnomalyModel

logger = logging.getLogger(__name__)


class TrainingPipeline:
    """Train and evaluate forensic anomaly detection models."""

    def __init__(self, models_dir: Optional[str] = None, output_dir: Optional[str] = None):
        models_dir = Path(models_dir) if models_dir else Path(__file__).parent.parent / "models"
        self.models_dir = models_dir
        self.output_dir = Path(output_dir) if output_dir else Path(__file__).parent.parent.parent / "training_results"
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def train(
        self,
        log_facts: List[Dict[str, Any]],
        labels: Optional[Dict[str, int]] = None,  # fact_id -> 0 (normal) / 1 (anomaly)
        contamination: float = 0.15,
        n_splits: int = 3
    ) -> Dict[str, Any]:
        """Train a new anomaly detection model."""
        logger.info(f"Training new model on {len(log_facts)} samples...")

        # Build feature matrix
        from .ml_model import ForensicAnomalyModel as FAM
        X, metadata = FAM.extract_features(log_facts)

        # Determine labels
        label_dict = {}
        for i, m in enumerate(metadata):
            label_dict[m["fact"].get("id", f"FACT-LOG-{i}")] = 0
        if labels:
            label_dict.update(labels)

        y = [label_dict.get(m["fact"].get("id", f"FACT-LOG-{i}"), 0) for i, m in enumerate(metadata)]

        # Split for evaluation
        if len(X) >= 4:
            X_train, X_test, y_train, y_test, meta_train, meta_test = train_test_split(
                X, y, metadata, test_size=0.3, random_state=42, stratify=y
            )
        else:
            X_train, X_test = X, X[:0]
            y_train, y_test = y, []
            meta_train, meta_test = metadata, []

        # Train
        model = ForensicAnomalyModel(contamination=contamination, n_estimators=100)
        model.fit(log_facts)

        # Evaluate if we have labels
        metrics = {}
        if y_test:
            raw_scores = model.model.decision_function(X_test)
            # Normalize to 0-1 (higher = more anomalous)
            scores = (raw_scores - raw_scores.min()) / (raw_scores.max() - raw_scores.min()) if raw_scores.max() != raw_scores.min() else raw_scores

            try:
                pred_labels = (scores > 0.5).astype(int)
                precision = precision_score(y_test, pred_labels, zero_division=0)
                recall = recall_score(y_test, pred_labels, zero_division=0)
                f1 = f1_score(y_test, pred_labels, zero_division=0)
                if len(set(y_test)) > 1 and len(set(pred_labels)) > 1:
                    auc = roc_auc_score(y_test, scores)
                else:
                    auc = 0.0
            except Exception as e:
                logger.warning(f"Evaluation error: {e}")
                precision, recall, f1, auc = 0.0, 0.0, 0.0, 0.0

            metrics = {
                "test_size": len(y_test),
                "precision": round(float(precision), 4),
                "recall": round(float(recall), 4),
                "f1_score": round(float(f1), 4),
                "roc_auc": round(float(auc), 4),
                "positive_class_distribution": {str(k): y_test.count(k) for k in set(y_test)}
            }
        else:
            metrics = {"note": "Unsupervised mode — no labeled data for evaluation metrics"}

        # Save model
        result = model.save_model(str(self.models_dir))

        report = {
            "status": "TRAINING_COMPLETE",
            "model_id": model.model_id,
            "created_at": model.created_at,
            "n_training_samples": len(X),
            "n_features": len(model.feature_names),
            "feature_names": model.feature_names,
            "contamination": contamination,
            "evaluation_metrics": metrics,
            "artifacts": result
        }

        # Write training report
        report_path = self.output_dir / f"training_report_{model.model_id}.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Training complete. Model {model.model_id}, report at {report_path}")
        return report

    def train_with_synthetic_labels(self, log_facts: List[Dict[str, Any]], contamination: float = 0.15) -> Dict[str, Any]:
        """
        Train using self-supervised synthetic labels for evaluation.
        Labels derived from high-severity actions / off-hours + external IP heuristics.
        Use with caution — evaluation metrics are indicative, not ground truth.
        """
        from .ml_model import ForensicAnomalyModel as FAM

        labels: Dict[str, int] = {}
        for fact in log_facts:
            text = (fact.get("raw_text") or fact.get("content") or "").upper()
            ip = FAM.extract_ip_from_text(text or "")
            sev = FAM.get_action_severity(text or "")
            is_external = bool(ip and not FAM.is_private_ip(ip))
            is_off_hours = fact.get("t_min") and self._is_off_hours(fact.get("t_min"))

            if sev >= 0.7 and (is_external or is_off_hours):
                labels[fact.get("id", str(fact.get("fact_id")))] = 1
            else:
                labels[fact.get("id", str(fact.get("fact_id")))] = 0

        return self.train(log_facts, labels=labels, contamination=contamination)

    @staticmethod
    def _is_off_hours(timestamp: str) -> bool:
        from .timeline_engine import parse_iso_datetime
        dt = parse_iso_datetime(timestamp)
        if not dt:
            return False
        hour = dt.hour + dt.minute / 60.0
        return hour >= 22.0 or hour < 6.0

    def list_models(self) -> List[Dict[str, Any]]:
        """List all persisted models."""
        models = []
        for manifest in sorted(self.models_dir.glob("manifest_*.json")):
            with open(manifest) as f:
                m = json.load(f)
            models.append({
                "model_id": m.get("model_id"),
                "created_at": m.get("created_at"),
                "algorithm": m.get("algorithm"),
                "n_training_samples": m.get("training_stats", {}).get("n_samples", 0),
                "manifest_path": str(manifest)
            })
        return models


# Backward-compatible singleton alias
def get_training_pipeline(models_dir: Optional[str] = None) -> TrainingPipeline:
    return TrainingPipeline(models_dir=models_dir)
