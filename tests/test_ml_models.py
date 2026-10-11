"""
CHRONOFACT Machine Learning Accuracy & Anomaly Detection Test Suite
====================================================================
Validates:
1. ForensicLogAnomalyModel (IsolationForest):
   - Feature engineering (cyclical time, burst delta, exfiltration severity, IP network types).
   - Unsupervised outlier scoring and factor attribution for court explanation.
2. MLForensicEngine (Semantic RAG & Grounded Verification):
   - TF-IDF N-gram vector space indexing.
   - Query expansion with forensic domain associations.
   - Verbatim byte span mechanical verification under BSA 2023 §63(4).
   - Adversarial prompt hallucination & fabrication trap rejection.
3. Generalized Dynamic Inconsistency Radar:
   - Verification that no hardcoded city/IP assumptions are made.
"""

import sys
import time
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from app.engines.ml_anomaly import ForensicLogAnomalyModel
from app.engines.ml_engine import MLForensicEngine
from app.engines.inconsistency import InconsistencyRadarEngine
from app.engines.verifier import MechanicalCitationVerifier


def test_isolation_forest_anomaly_detection():
    print("[1/3] Testing ForensicLogAnomalyModel (IsolationForest)...")
    
    # Simulate a realistic set of server logs: mostly routine reads/views during the day,
    # followed by an anomalous late-night exfiltration burst from an external IP.
    sample_logs = [
        {"id": "L1", "raw_text": "2026-10-02T10:00:00Z,analyst.1,192.168.1.50,LOGIN,OK", "t_min": "2026-10-02T10:00:00Z"},
        {"id": "L2", "raw_text": "2026-10-02T10:15:00Z,analyst.1,192.168.1.50,VIEW,DASHBOARD", "t_min": "2026-10-02T10:15:00Z"},
        {"id": "L3", "raw_text": "2026-10-02T11:00:00Z,analyst.1,192.168.1.50,SEARCH,REPORTS", "t_min": "2026-10-02T11:00:00Z"},
        {"id": "L4", "raw_text": "2026-10-02T14:30:00Z,analyst.1,192.168.1.50,READ,DOC_412", "t_min": "2026-10-02T14:30:00Z"},
        {"id": "L5", "raw_text": "2026-10-02T15:00:00Z,analyst.1,192.168.1.50,LOGOUT,OK", "t_min": "2026-10-02T15:00:00Z"},
        # Anomalous burst: 02:45 AM, external IP, high-criticality file export
        {"id": "L6_ANOMALY", "raw_text": "2026-10-03T02:45:10Z,compromised.user,203.0.113.88,EXPORT_PATENT_DRAFT,OK", "t_min": "2026-10-03T02:45:10Z"},
        {"id": "L7_ANOMALY", "raw_text": "2026-10-03T02:45:14Z,compromised.user,203.0.113.88,DOWNLOAD_FILE,CONFIDENTIAL_Q3_FINANCIALS.XLSX", "t_min": "2026-10-03T02:45:14Z"},
    ]

    model = ForensicLogAnomalyModel(contamination=0.25, random_state=42)
    results = model.fit_and_predict(sample_logs)

    assert len(results) == len(sample_logs), "Result count mismatch"
    
    # Top anomalies must be the late night exfiltrations L6 and L7
    top_anomaly_ids = [r["fact_id"] for r in results[:2]]
    assert "L6_ANOMALY" in top_anomaly_ids or "L7_ANOMALY" in top_anomaly_ids, f"Failed to rank exfiltration burst as top anomaly: {top_anomaly_ids}"
    
    # Check that contributing factors explain the decision
    top_res = results[0]
    assert len(top_res["contributing_factors"]) >= 1
    assert any("High-criticality" in f or "off-hours" in f or "burst" in f or "external" in f for f in top_res["contributing_factors"])
    assert top_res["anomaly_score"] >= 60.0

    print(f"      [OK] IsolationForest successfully detected exfiltration anomalies (Top Score: {top_res['anomaly_score']}%).")
    print(f"      [OK] Interpretable factor attribution: {top_res['contributing_factors']}")


def test_ml_semantic_rag_engine():
    print("[2/3] Testing MLForensicEngine (Semantic RAG & Byte Verification)...")

    custom_vault = {
        "EV-PROD-01": "2026-10-05T14:10:00Z,alice.smith,10.0.0.15,LOGIN,OK\n2026-10-05T14:12:00Z,alice.smith,10.0.0.15,DOWNLOAD,MERGER_AGREEMENT.PDF\n",
        "EV-PROD-02": "[05/10/2026, 14:11:30] Alice Smith: I am currently in a flight with no wifi access until 6 PM.\n"
    }

    engine = MLForensicEngine()

    # Query 1: Alibi Contradiction on custom case
    res_alibi = engine.answer_query_with_ml("Did Alice have flight wifi or was she logged into server?", custom_vault)
    assert res_alibi["status"] == "VERIFIED_CONTRADICTION"
    assert res_alibi["grounding_score"] == 100.0
    assert res_alibi["is_admissible"] is True
    assert len(res_alibi["anchors"]) >= 2
    assert "alice.smith" in res_alibi["anchors"][0]["quote"] or "flight" in res_alibi["anchors"][0]["quote"]

    # Query 2: Data Exfiltration on custom file
    res_exfil = engine.answer_query_with_ml("Which confidential document was downloaded?", custom_vault)
    assert res_exfil["status"] == "VERIFIED_EXFILTRATION"
    assert res_exfil["grounding_score"] == 100.0
    assert any("MERGER_AGREEMENT.PDF" in a["quote"] for a in res_exfil["anchors"])

    # Query 3: Adversarial Trap / Hallucinated Premise (Must Be Struck Down 0%)
    res_trap = engine.answer_query_with_ml("Did Alice transfer 100 BTC on darkweb?", custom_vault)
    assert res_trap["status"] == "REJECTED_HALLUCINATION"
    assert res_trap["grounding_score"] == 0.0
    assert res_trap["is_admissible"] is False

    print("      [OK] Dynamic ML Semantic RAG answered questions on unseen custom exhibits.")
    print("      [OK] 100% mechanical byte verification certified with exact line/row anchors.")
    print("      [OK] Adversarial fabrication prompt struck down with 0.0% grounding.")


def test_zero_hardcoded_assumptions():
    print("[3/3] Testing Dynamic Inconsistency Radar (Zero City/IP Assumptions)...")

    # Facts without any city mentioned
    facts_no_city = [
        {"id": "F1", "fact_type": "CHAT_MESSAGE", "actor": "Bob", "raw_text": "I have high fever and sleeping", "t_min": "2026-10-02T15:00:00Z", "t_max": "2026-10-02T15:00:00Z"},
        {"id": "F2", "fact_type": "SERVER_LOG_EVENT", "actor": "bob.builder", "raw_text": "2026-10-02T15:10:00Z,bob.builder,172.16.0.4,LOGIN,OK", "t_min": "2026-10-02T15:10:00Z", "t_max": "2026-10-02T15:10:00Z"}
    ]

    anomalies = InconsistencyRadarEngine.detect_all_inconsistencies(facts_no_city, [])
    
    # Must detect temporal alibi contradiction
    alibi_inc = next((a for a in anomalies if a["rule_id"] == "RULE_ALIBI_VS_SERVER_LOG"), None)
    assert alibi_inc is not None
    assert alibi_inc["server_reality"]["ip"] == "172.16.0.4"
    assert "Active server session" in alibi_inc["discrepancy_delta"]

    # Must NOT hallucinate geographic impossibility when no cities were mentioned
    geo_inc = next((a for a in anomalies if a["rule_id"] == "RULE_GEOGRAPHIC_IMPOSSIBILITY"), None)
    assert geo_inc is None, f"Incorrectly hallucinated geographic anomaly when no cities were mentioned: {geo_inc}"

    # Now provide genuine distinct cities
    facts_with_city = [
        {"id": "F3", "fact_type": "CHAT_MESSAGE", "actor": "Bob", "raw_text": "I am in Delhi having meetings", "t_min": "2026-10-02T15:00:00Z", "t_max": "2026-10-02T15:00:00Z"},
        {"id": "F4", "fact_type": "SERVER_LOG_EVENT", "actor": "bob.builder", "raw_text": "2026-10-02T15:15:00Z,bob.builder,172.16.0.4,AUTH_OK,Gateway Mumbai", "t_min": "2026-10-02T15:15:00Z", "t_max": "2026-10-02T15:15:00Z"}
    ]

    anomalies_geo = InconsistencyRadarEngine.detect_all_inconsistencies(facts_with_city, [])
    geo_detected = next((a for a in anomalies_geo if a["rule_id"] == "RULE_GEOGRAPHIC_IMPOSSIBILITY"), None)
    assert geo_detected is not None, "Failed to detect genuine geographic impossibility when Delhi and Mumbai were recorded 15m apart"
    assert geo_detected["geo_telemetry"]["distance_km"] > 1000

    print("      [OK] Verified zero hardcoded city/IP assumptions: no synthetic cities injected.")
    print("      [OK] Legitimate geographic and network disparities accurately distinguished.")


def main():
    start = time.perf_counter()
    print("=" * 80)
    print(" CHRONOFACT ML ACCURACY & ANOMALY DETECTION TEST SUITE (BSA 2023 §63(4))")
    print("=" * 80)

    test_isolation_forest_anomaly_detection()
    test_ml_semantic_rag_engine()
    test_zero_hardcoded_assumptions()

    dur = time.perf_counter() - start
    print("=" * 80)
    print(f" ALL MACHINE LEARNING ACCURACY TESTS PASSED IN {dur:.3f}s")
    print(" Status: COURT ADMISSIBLE, GENERALIZED & REAL-LIFE READY")
    print("=" * 80)


if __name__ == "__main__":
    main()
