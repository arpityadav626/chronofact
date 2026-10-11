"""
CHRONOFACT Production ML Model Module
======================================
Trainable, persistable forensic log anomaly detector with model versioning,
evaluation metrics, and court-explainable predictions.
"""

import os
import json
import logging
import pickle
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone

import numpy as np
from sklearn.ensemble import IsolationForest

logger = logging.getLogger(__name__)


class ForensicAnomalyModel:
    """
    Production-grade forensic log anomaly detector.

    Features:
    1. IsolationForest for unsupervised behavioral outlier detection
    2. Automatic feature engineering (temporal, burst, severity, network)
    3. Model persistence to disk with integrity hashing
    4. Prediction explainability (contributing factors)
    5. Retraining support with versioned model artifacts

    Fits BSA 2023 §63(4) requirement that forensic analytics be
    reproducible and verifiable.
    """

    def __init__(
        self,
        contamination: float = 0.15,
        random_state: int = 42,
        n_estimators: int = 100,
        model_path: Optional[str] = None
    ):
        """
        Initialize the forensic anomaly detection model.

        Args:
            contamination: Expected proportion of anomalies in training data
            random_state: Reproducibility seed
            n_estimators: Number of trees in the forest
            model_path: Optional path to load a persisted model from
        """
        self.contamination = contamination
        self.random_state = random_state
        self.n_estimators = n_estimators
        self.feature_names = [
            "hour_sin", "hour_cos", "is_off_hours",
            "delta_seconds_log1p", "action_severity",
            "is_private_ip", "text_length_norm"
        ]
        self.model: Optional[IsolationForest] = None
        self.training_stats: Optional[Dict[str, Any]] = None
        self.model_id: Optional[str] = None
        self.created_at: Optional[str] = None

        if model_path:
            self.load_model(str(model_path))

    # ---------------------------- Feature Engineering ----------------------------

    @staticmethod
    def extract_features(log_facts: List[Dict[str, Any]]) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
        """Extract numeric feature matrix from raw log facts."""
        from .timeline_engine import parse_iso_datetime

        if not log_facts:
            return np.empty((0, len(["hour_sin", "hour_cos", "is_off_hours",
                                     "delta_seconds_log1p", "action_severity",
                                     "is_private_ip", "text_length_norm"])), dtype=float), []

        parsed_items = []
        for f in log_facts:
            dt = parse_iso_datetime(f.get("t_min") or f.get("timestamp") or "")
            parsed_items.append((dt, f))

        parsed_items.sort(key=lambda x: (x[0] is None, x[0] if x[0] else datetime.min.replace(tzinfo=timezone.utc)))

        features = []
        metadata = []
        prev_dt: Optional[datetime] = None

        for dt, fact in parsed_items:
            raw_text = fact.get("raw_text") or fact.get("content") or ""

            # 1. Cyclical temporal features (24-hour)
            if dt:
                hour = dt.hour + dt.minute / 60.0 + dt.second / 3600.0
                hour_sin = np.sin(2.0 * np.pi * hour / 24.0)
                hour_cos = np.cos(2.0 * np.pi * hour / 24.0)
                is_off_hours = 1.0 if (hour >= 22.0 or hour < 6.0) else 0.0
            else:
                hour_sin, hour_cos, is_off_hours = 0.0, 1.0, 0.0

            # 2. Inter-event delta (burst/velocity)
            if dt and prev_dt:
                delta_sec = max(0.0, (dt - prev_dt).total_seconds())
            else:
                delta_sec = 60.0
            prev_dt = dt
            delta_seconds_log1p = np.log1p(min(delta_sec, 86400.0))

            # 3. Action criticality weight
            severity = ForensicAnomalyModel.get_action_severity(raw_text)

            # 4. IP network classification
            ip = ForensicAnomalyModel.extract_ip_from_text(raw_text)
            is_priv = 1.0 if (ip and ForensicAnomalyModel.is_private_ip(ip)) else 0.0

            # 5. Text length normalization (payloads / injection attempts)
            text_len_norm = min(1.0, len(raw_text) / 200.0)

            row = [hour_sin, hour_cos, is_off_hours, delta_seconds_log1p,
                   severity, is_priv, text_len_norm]
            features.append(row)
            metadata.append({
                "fact": fact, "dt": dt, "ip": ip, "severity": severity,
                "is_off_hours": bool(is_off_hours), "delta_sec": delta_sec,
                "raw_text": raw_text
            })

        return np.array(features, dtype=float), metadata

    @staticmethod
    def get_action_severity(text: str) -> float:
        """Forensic action criticality weights (court-explainable)."""
        text_upper = text.upper()
        weights = {
            "EXFILTRATE": 1.0, "EXPORT_PATENT_DRAFT": 0.95, "DROP": 0.95,
            "PRIVILEGE_ESCALATE": 0.95, "DELETE": 0.9, "SUDO": 0.8,
            "EXPORT": 0.85, "TRANSFER": 0.8, "PASSWORD_RESET": 0.7,
            "DOWNLOAD_FILE": 0.75, "DOWNLOAD": 0.7,
            "LOGIN": 0.2, "AUTH": 0.2, "QUERY": 0.2, "SEARCH": 0.15,
            "VIEW": 0.1, "READ": 0.1
        }
        return max((weights[kw] for kw in weights if kw in text_upper), default=0.1)

    @staticmethod
    def extract_ip_from_text(text: str) -> Optional[str]:
        import re
        match = re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", text)
        return match.group(0) if match else None

    @staticmethod
    def is_private_ip(ip: str) -> bool:
        parts = ip.split(".")
        if len(parts) != 4:
            return False
        try:
            p0, p1 = int(parts[0]), int(parts[1])
            return p0 == 10 or (p0 == 172 and 16 <= p1 <= 31) or (p0 == 192 and p1 == 168) or p0 == 127
        except ValueError:
            return False

    # ---------------------------- Training ----------------------------

    def fit(self, log_facts: List[Dict[str, Any]]) -> "ForensicAnomalyModel":
        """Train the model on forensic log facts."""
        X, self._training_metadata = self.extract_features(log_facts)

        if len(X) < 2:
            logger.warning("Too few samples for model training")
            return self

        # Adaptive contamination based on sample size
        eff_cont = min(0.4, max(0.05, self.contamination))

        self.model = IsolationForest(
            contamination=eff_cont,
            random_state=self.random_state,
            n_estimators=self.n_estimators,
            n_jobs=-1
        )
        self.model.fit(X)

        self.training_stats = {
            "n_samples": len(X),
            "n_features": len(self.feature_names),
            "feature_names": self.feature_names,
            "effective_contamination": eff_cont,
            "training_timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "algorithm": "IsolationForest",
            "hyperparameters": {
                "contamination": self.contamination,
                "random_state": self.random_state,
                "n_estimators": self.n_estimators
            }
        }
        self.model_id = self._compute_model_id()
        self.created_at = self.training_stats["training_timestamp_utc"]
        logger.info(f"Model trained on {len(X)} samples, model_id={self.model_id}")
        return self

    def _compute_model_id(self) -> str:
        """Compute deterministic model ID from hyperparameters + training data hash."""
        data = json.dumps({
            "hyperparameters": self.training_stats["hyperparameters"] if self.training_stats else {},
            "n_samples": self.training_stats["n_samples"] if self.training_stats else 0
        }, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()[:12]

    # ---------------------------- Prediction ----------------------------

    def predict(self, log_facts: List[Dict[str, Any]], explain: bool = True) -> List[Dict[str, Any]]:
        """Predict anomalies for new log facts with explanations."""
        if self.model is None:
            raise RuntimeError("Model not trained. Call fit() first.")

        X, metadata = self.extract_features(log_facts)

        if len(X) < 2:
            return []

        raw_scores = self.model.decision_function(X)
        preds = self.model.predict(X)

        min_s, max_s = float(raw_scores.min()), float(raw_scores.max())
        spread = max_s - min_s if max_s > min_s else 1.0

        results = []
        for i in range(len(X)):
            norm_score = round((1.0 - (raw_scores[i] - min_s) / spread) * 100.0, 1)
            is_anomaly = bool(preds[i] == -1 or norm_score >= 70.0 or metadata[i]["severity"] >= 0.85)

            factors = []
            if metadata[i]["severity"] >= 0.7:
                factors.append(f"High-criticality operation (weight {metadata[i]['severity']:.2f})")
            if metadata[i]["is_off_hours"]:
                factors.append("Executed during off-hours (22:00 - 06:00)")
            if metadata[i]["delta_sec"] < 5.0 and i > 0:
                factors.append(f"High burst rate ({metadata[i]['delta_sec']:.1f}s after previous action)")
            if metadata[i]["ip"] and not ForensicAnomalyModel.is_private_ip(metadata[i]["ip"]):
                factors.append(f"Public external IP connection ({metadata[i]['ip']})")
            if not factors:
                factors.append("Behavioral deviation detected by Isolation Forest")

            results.append({
                "fact_id": metadata[i]["fact"].get("id", f"FACT-LOG-{i}"),
                "evidence_id": metadata[i]["fact"].get("evidence_id", "EV-UNKNOWN"),
                "locator": metadata[i]["fact"].get("locator", f"Row {i+1}"),
                "raw_text": metadata[i]["raw_text"],
                "timestamp": metadata[i]["fact"].get("t_min") or "",
                "anomaly_score": norm_score,
                "is_anomaly": is_anomaly,
                "confidence_level": "ML_ISOLATION_FOREST",
                "severity": "CRITICAL" if norm_score >= 80 else "HIGH" if norm_score >= 60 else "MEDIUM" if norm_score >= 40 else "LOW",
                "contributing_factors": factors
            })

        results.sort(key=lambda x: x["anomaly_score"], reverse=True)
        return results

    # ---------------------------- Persistence ----------------------------

    def save_model(self, output_dir: Optional[str] = None) -> Dict[str, str]:
        """Persist model and metadata to disk with integrity hash."""
        if self.model is None:
            raise RuntimeError("Cannot save untrained model.")

        output_dir = Path(output_dir) if output_dir else (Path(__file__).parent.parent / "models")
        output_dir.mkdir(parents=True, exist_ok=True)

        now = datetime.now(timezone.utc).isoformat()
        model_id = self.model_id or hashlib.sha256(now.encode()).hexdigest()[:12]

        # Serialize model bytes
        model_bytes = pickle.dumps(self.model)
        model_hash = hashlib.sha256(model_bytes).hexdigest()

        # Save model file
        model_path = output_dir / f"model_{model_id}.pkl"
        with open(model_path, "wb") as f:
            f.write(model_bytes)

        # Save metadata with manifest
        model_stem = model_path.stem  # e.g. "model_bb4c9d7c4de5"
        manifest = {
            "model_id": model_id,
            "created_at": self.created_at or now,
            "algorithm": "IsolationForest",
            "feature_names": self.feature_names,
            "training_stats": self.training_stats,
            "model_file": model_path.name,
            "model_hash_sha256": model_hash,
            "signature": f"CHRONOFACT-FORENSIC-ML-{model_id}"
        }
        manifest_path = output_dir / f"manifest_{model_stem}.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        logger.info(f"Model saved: {model_path} (hash={model_hash[:16]}...)")
        return {"model_path": str(model_path), "manifest_path": str(manifest_path)}

    def load_model(self, path: str) -> "ForensicAnomalyModel":
        """Load a persisted model from disk."""
        path = Path(path).resolve()  # normalize absolute/relative paths
        if path.is_dir():
            # Find latest manifest
            manifests = sorted(path.glob("manifest_*.json"))
            if not manifests:
                raise FileNotFoundError(f"No model manifest found in {path}")
            with open(manifests[-1]) as f:
                manifest = json.load(f)
            model_path = path / manifest["model_file"]
        else:
            # Handle both manifest paths and model paths directly
            if path.name.startswith("manifest_"):
                with open(path) as f:
                    manifest = json.load(f)
                model_path = path.parent / manifest["model_file"]
            else:
                # Model path: manifest_{model_file_stem}.json
                manifest_path = path.parent / f"manifest_{path.stem}.json"
                if manifest_path.exists():
                    with open(manifest_path) as f:
                        manifest = json.load(f)
                    model_path = manifest_path.parent / manifest["model_file"]
                else:
                    model_path = path

        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")

        with open(model_path, "rb") as f:
            model_bytes = f.read()

        # Integrity check
        computed_hash = hashlib.sha256(model_bytes).hexdigest()
        manifest_file_name = str(Path(manifest["model_file"]).with_suffix(".json"))
        manifest_candidate = model_path.parent / f"manifest_{manifest_file_name}"
        if model_path.parent.exists() and manifest_candidate.exists():
            with open(manifest_candidate) as f:
                saved_hash = json.load(f).get("model_hash_sha256")
            if saved_hash and computed_hash != saved_hash:
                raise ValueError(f"Model file corrupted: hash mismatch {computed_hash[:16]} vs {saved_hash[:16]}")

        self.model = pickle.loads(model_bytes)
        if "manifest" in locals() and manifest:
            self.training_stats = manifest.get("training_stats")
            self.model_id = manifest.get("model_id")
            self.created_at = manifest.get("created_at")
        logger.info(f"Model loaded: {model_path} (id={self.model_id})")
        return self

    def get_status(self) -> Dict[str, Any]:
        """Return model health and configuration status."""
        if self.model is None:
            return {"status": "NOT_TRAINED", "model_id": None}
        return {
            "status": "READY",
            "model_id": self.model_id,
            "created_at": self.created_at,
            "algorithm": "IsolationForest",
            "n_estimators": self.n_estimators,
            "feature_names": self.feature_names,
            "training_samples": self.training_stats["n_samples"] if self.training_stats else 0
        }


# Re-export TrainingPipeline for backwards compatibility
from .training_pipeline import TrainingPipeline
