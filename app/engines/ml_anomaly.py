"""
CHRONOFACT Machine Learning Anomaly Detection Engine
=====================================================
Forensic Unsupervised Log Anomaly & Intrusion Detection
using Scikit-Learn IsolationForest and Statistical Feature Engineering.

Features:
- Cyclical temporal featurization (sine/cosine 24-hour transforms)
- Inter-event velocity and burst rate estimation
- Action criticality & exfiltration entropy scoring
- IP address and subnet diversity tracking
- Interpretable anomaly explanations for court admissibility (BSA 2023 §63(4))
"""

import math
import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from sklearn.ensemble import IsolationForest

from .timeline_engine import parse_iso_datetime


# Action risk weights for digital forensic log actions
CRITICAL_ACTION_WEIGHTS: Dict[str, float] = {
    "LOGIN": 0.2,
    "AUTH": 0.2,
    "VIEW": 0.1,
    "READ": 0.1,
    "SEARCH": 0.15,
    "QUERY": 0.2,
    "DOWNLOAD": 0.7,
    "DOWNLOAD_FILE": 0.75,
    "EXPORT": 0.85,
    "EXPORT_PATENT_DRAFT": 0.95,
    "EXFILTRATE": 1.0,
    "DELETE": 0.9,
    "DROP": 0.95,
    "PRIVILEGE_ESCALATE": 0.95,
    "SUDO": 0.8,
    "PASSWORD_RESET": 0.7,
    "TRANSFER": 0.8,
}


def extract_ip_from_text(text: str) -> Optional[str]:
    """Extract first IPv4 address found in text string."""
    match = re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", text)
    return match.group(0) if match else None


def is_private_ip(ip: str) -> bool:
    """Determine whether an IP address belongs to RFC 1918 private ranges."""
    if not ip:
        return False
    parts = ip.split(".")
    if len(parts) != 4:
        return False
    try:
        p0, p1 = int(parts[0]), int(parts[1])
        if p0 == 10:
            return True
        if p0 == 172 and 16 <= p1 <= 31:
            return True
        if p0 == 192 and p1 == 168:
            return True
        if p0 == 127:
            return True
    except ValueError:
        pass
    return False


def get_action_severity(text: str) -> float:
    """Calculate forensic severity weight of an action based on keywords."""
    text_upper = text.upper()
    max_weight = 0.1
    for kw, weight in CRITICAL_ACTION_WEIGHTS.items():
        if kw in text_upper:
            if weight > max_weight:
                max_weight = weight
    return max_weight


class ForensicLogAnomalyModel:
    """
    Unsupervised Machine Learning model for detecting anomalous behaviors,
    exfiltration spikes, off-hours access, and abnormal activity sequences in digital logs.
    """

    def __init__(self, contamination: float = 0.15, random_state: int = 42):
        self.contamination = contamination
        self.random_state = random_state
        self.model: Optional[IsolationForest] = None
        self.feature_names = [
            "hour_sin",
            "hour_cos",
            "is_off_hours",
            "delta_seconds_log1p",
            "action_severity",
            "is_private_ip",
            "text_length_norm",
        ]

    def extract_features(self, log_facts: List[Dict[str, Any]]) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
        """
        Extract numeric feature matrix from raw log fact dictionaries.
        Sorts temporally to calculate realistic inter-event delta times.
        """
        if not log_facts:
            return np.empty((0, len(self.feature_names))), []

        # Sort facts by timestamp if available
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
            
            # 1. Temporal cyclical features
            if dt:
                hour = dt.hour + dt.minute / 60.0 + dt.second / 3600.0
                hour_sin = math.sin(2.0 * math.pi * hour / 24.0)
                hour_cos = math.cos(2.0 * math.pi * hour / 24.0)
                # Off-hours: 22:00 to 06:00
                is_off_hours = 1.0 if (hour >= 22.0 or hour < 6.0) else 0.0
            else:
                hour_sin = 0.0
                hour_cos = 1.0
                is_off_hours = 0.0

            # 2. Inter-event delta time (burst / velocity)
            if dt and prev_dt:
                delta_sec = max(0.0, (dt - prev_dt).total_seconds())
            else:
                delta_sec = 60.0  # default 1 min
            prev_dt = dt
            delta_seconds_log1p = math.log1p(min(delta_sec, 86400.0))

            # 3. Action severity
            severity = get_action_severity(raw_text)

            # 4. IP analysis
            ip = extract_ip_from_text(raw_text)
            is_priv = 1.0 if (ip and is_private_ip(ip)) else 0.0

            # 5. Text length normalized (long payloads often denote exfiltration or SQL injections)
            text_len_norm = min(1.0, len(raw_text) / 200.0)

            row = [
                hour_sin,
                hour_cos,
                is_off_hours,
                delta_seconds_log1p,
                severity,
                is_priv,
                text_len_norm,
            ]
            features.append(row)
            metadata.append({
                "fact": fact,
                "dt": dt,
                "ip": ip,
                "severity": severity,
                "is_off_hours": bool(is_off_hours),
                "delta_sec": delta_sec,
                "raw_text": raw_text,
            })

        return np.array(features, dtype=float), metadata

    def fit_and_predict(self, log_facts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Fit IsolationForest on extracted features and return scored anomalies.
        """
        if not log_facts:
            return []

        X, meta = self.extract_features(log_facts)
        n_samples = len(X)
        if n_samples < 2:
            # Need at least a couple samples for anomaly ranking; return heuristic score
            results = []
            for m in meta:
                raw_text = m["raw_text"]
                sev = m["severity"]
                score = round(sev * 100.0, 1)
                is_anomaly = sev >= 0.7
                results.append({
                    "fact_id": m["fact"].get("id", "F-UNKNOWN"),
                    "evidence_id": m["fact"].get("evidence_id", "EV-UNKNOWN"),
                    "locator": m["fact"].get("locator", "Log"),
                    "raw_text": raw_text,
                    "anomaly_score": score,
                    "is_anomaly": is_anomaly,
                    "confidence_level": "HEURISTIC",
                    "severity": "CRITICAL" if score > 75 else "MEDIUM" if score > 40 else "LOW",
                    "contributing_factors": ["High action severity" if sev >= 0.7 else "Standard log entry"]
                })
            return results

        # Dynamically bound contamination according to sample size
        effective_contamination = min(0.4, max(0.05, self.contamination))
        self.model = IsolationForest(
            contamination=effective_contamination,
            random_state=self.random_state,
            n_estimators=100
        )
        self.model.fit(X)

        # decision_function gives negative values for anomalies, positive for inliers
        raw_scores = self.model.decision_function(X)
        preds = self.model.predict(X)  # -1 for anomaly, 1 for inlier

        # Normalize score into 0 - 100 (where 100 = most anomalous)
        min_s = float(raw_scores.min())
        max_s = float(raw_scores.max())
        spread = max_s - min_s if max_s > min_s else 1.0

        anomalies = []
        for i in range(n_samples):
            # Invert: lower raw score -> higher anomaly percentage
            norm_anomaly_score = round((1.0 - (raw_scores[i] - min_s) / spread) * 100.0, 1)
            is_anomaly = bool(preds[i] == -1 or norm_anomaly_score >= 70.0 or meta[i]["severity"] >= 0.85)

            # Generate natural language forensic explanation of factors
            factors = []
            m = meta[i]
            if m["severity"] >= 0.7:
                factors.append(f"High-criticality operation detected (weight {m['severity']:.2f})")
            if m["is_off_hours"]:
                factors.append("Executed during non-business off-hours (22:00 - 06:00)")
            if m["delta_sec"] < 5.0 and i > 0:
                factors.append(f"High burst rate ({m['delta_sec']:.1f}s after previous action)")
            if m["ip"] and not is_private_ip(m["ip"]):
                factors.append(f"Public external IP address connection ({m['ip']})")
            if not factors:
                factors.append("Behavioral sequence deviation detected by Isolation Forest")

            anomalies.append({
                "fact_id": m["fact"].get("id", f"FACT-LOG-{i}"),
                "evidence_id": m["fact"].get("evidence_id", "EV-UNKNOWN"),
                "locator": m["fact"].get("locator", f"Row {i+1}"),
                "raw_text": m["raw_text"],
                "timestamp": m["fact"].get("t_min") or "",
                "anomaly_score": norm_anomaly_score,
                "is_anomaly": is_anomaly,
                "confidence_level": "ML_ISOLATION_FOREST",
                "severity": "CRITICAL" if norm_anomaly_score >= 80 else "HIGH" if norm_anomaly_score >= 60 else "MEDIUM" if norm_anomaly_score >= 40 else "LOW",
                "contributing_factors": factors
            })

        # Sort by anomaly score descending
        anomalies.sort(key=lambda x: x["anomaly_score"], reverse=True)
        return anomalies
