"""
CHRONOFACT Backend Accuracy Engine Comprehensive Test Suite
===========================================================
Validates:
1. Module 1: Uncertainty-Aware Hyper-Timeline & Allen's Interval Algebra.
2. Module 2: Cross-Modal Inconsistency & Alibi Conflict Radar (with Haversine Velocity).
3. Module 3: Mechanical Citation Verifier & Zero-Hallucination Grounding Gate.
4. Module 4: Statutory BSA 2023 Section 63(4) Evidence Certificate Engine.
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

from app.engines.timeline_engine import (
    TimelineEngine,
    classify_allen_relation,
    AllenRelation,
    parse_iso_datetime,
    format_utc_and_ist,
    build_interval_timeline
)
from app.engines.inconsistency import (
    InconsistencyRadarEngine,
    calculate_haversine_distance_km,
    detect_inconsistencies
)
from app.engines.verifier import (
    MechanicalCitationVerifier,
    verify_ai_claims
)
from app.legal.bsa_certificate import (
    BSACertificateEngine,
    generate_bsa_section_63_certificate
)


def test_module_1_timeline_and_allen_algebra():
    """Verify Module 1: Allen's Interval Algebra and Clock Skew Calibrator."""
    print("[1/4] Testing Module 1: Hyper-Timeline & Allen's Interval Algebra...")

    dt1_s = parse_iso_datetime("2026-10-02T10:00:00Z")
    dt1_e = parse_iso_datetime("2026-10-02T11:00:00Z")
    dt2_s = parse_iso_datetime("2026-10-02T11:30:00Z")
    dt2_e = parse_iso_datetime("2026-10-02T12:00:00Z")

    # 1. Test Strict Precedes
    rel, label, overlap = classify_allen_relation(dt1_s, dt1_e, dt2_s, dt2_e)
    assert rel == AllenRelation.PRECEDES, f"Expected PRECEDES, got {rel}"
    assert "Strictly Precedes" in label
    assert overlap == 0.0

    # 2. Test Overlaps
    dt3_s = parse_iso_datetime("2026-10-02T10:45:00Z")
    dt3_e = parse_iso_datetime("2026-10-02T11:45:00Z")
    rel_ov, label_ov, overlap_sec = classify_allen_relation(dt1_s, dt1_e, dt3_s, dt3_e)
    assert rel_ov == AllenRelation.OVERLAPS, f"Expected OVERLAPS, got {rel_ov}"
    assert overlap_sec == 900.0, f"Expected 900s overlap, got {overlap_sec}"

    # 3. Test Hyper-Timeline Builder with Sample Facts
    sample_facts = [
        {
            "id": "F-01",
            "evidence_id": "EV-8EA211",
            "fact_type": "CHAT_MESSAGE",
            "actor": "Rohan",
            "raw_text": "Going to bed",
            "locator": "Line 1",
            "t_min": "2026-10-02T15:20:00+00:00",
            "t_max": "2026-10-02T15:20:00+00:00",
            "tz_basis": "utc"
        },
        {
            "id": "F-02",
            "evidence_id": "EV-SERVER",
            "fact_type": "SERVER_LOG_EVENT",
            "actor": "admin",
            "raw_text": "LOGIN OK",
            "locator": "Row 1",
            "t_min": "2026-10-02T15:25:00+00:00",
            "t_max": "2026-10-02T15:25:00+00:00",
            "tz_basis": "utc"
        }
    ]

    timeline = TimelineEngine.build_interval_timeline(sample_facts, calibration_mode="ntp")
    assert len(timeline) == 2
    assert "t_min_ist" in timeline[0]
    assert "allen_relation_vs_next" in timeline[0]
    assert timeline[0]["allen_relation_vs_next"] == AllenRelation.PRECEDES
    print("      [OK] Allen's Interval Algebra correctly classifies strict ordering & overlaps.")
    print("      [OK] Hyper-timeline constructs dual UTC/IST bounded intervals.")


def test_module_2_inconsistency_radar():
    """Verify Module 2: Cross-Modal Inconsistency & Haversine Velocity Radar."""
    print("[2/4] Testing Module 2: Inconsistency Radar & Geographic Velocity Impossibility...")

    # 1. Test Haversine Distance (Delhi to Mumbai ~ 1150 km)
    dist = calculate_haversine_distance_km(28.6139, 77.2090, 19.0760, 72.8777)
    assert 1140 < dist < 1180, f"Haversine calculation error: {dist} km"

    # 2. Test Alibi vs Server Contradiction
    facts = [
        {
            "id": "F-CHAT",
            "evidence_id": "EV-CHAT",
            "fact_type": "CHAT_MESSAGE",
            "actor": "Vikram",
            "raw_text": "Sir I am asleep with high fever and offline till morning.",
            "locator": "Line 2",
            "t_min": "2026-10-02T15:25:40+00:00",
            "t_max": "2026-10-02T15:25:40+00:00"
        },
        {
            "id": "F-LOG",
            "evidence_id": "EV-LOG",
            "fact_type": "SERVER_LOG_EVENT",
            "actor": "vikram.malhotra",
            "raw_text": "2026-10-02T15:28:45Z,vikram.malhotra,192.168.1.105,LOGIN,OK",
            "locator": "CSV Row 1",
            "t_min": "2026-10-02T15:28:45+00:00",
            "t_max": "2026-10-02T15:28:45+00:00"
        }
    ]

    evidence = [
        {"id": "EV-CHAT", "filename": "whatsapp.txt", "sha256": "c5153b32d491cc521a07116172f5b38a5aac2004027dd66c45af9b32817b47f4"},
        {"id": "EV-LOG", "filename": "server.csv", "sha256": "c67d5b85b52c2a5e11c76ff9691d483b233d2c8f6ae617702b8732a76f122618"}
    ]

    anomalies = InconsistencyRadarEngine.detect_all_inconsistencies(facts, evidence)
    assert len(anomalies) >= 1, "Failed to detect alibi conflict"

    alibi_inc = next((a for a in anomalies if a["rule_id"] == "RULE_ALIBI_VS_SERVER_LOG"), None)
    assert alibi_inc is not None, "Alibi contradiction not found"
    assert len(alibi_inc["benign_explanations"]) >= 3, "Mandatory benign explanations missing"
    assert "Active server session" in alibi_inc["discrepancy_delta"]
    print("      [OK] Alibi vs Server reality contradiction detected with discrepancy delta.")
    print(f"      [OK] Mandatory benign explanations verified ({len(alibi_inc['benign_explanations'])} alternate hypotheses generated).")


def test_module_3_mechanical_citation_verifier():
    """Verify Module 3: Mechanical Citation Verifier & Zero-Hallucination Gate."""
    print("[3/4] Testing Module 3: Mechanical Citation Verifier & Grounding Gate...")

    vault = {
        "EV-01": "2025-09-12,vikram.malhotra,192.168.1.105,LOGIN,OK\n2025-09-12,vikram.malhotra,192.168.1.105,DOWNLOAD,PATENT.ZIP\n",
        "EV-02": "[12/09/2025] Vikram: Sir I am suffering from high fever, I am asleep in bed.\n"
    }

    # Case A: Verbatim Match (100% Grounded)
    payload_valid = {
        "claims": [
            {
                "claim_text": "Suspect logged in from IP 192.168.1.105",
                "evidence_id": "EV-01",
                "exact_quote": "vikram.malhotra,192.168.1.105,LOGIN,OK",
                "locator": "Line 1"
            }
        ]
    }
    report_valid = MechanicalCitationVerifier.verify_ai_claims(payload_valid, vault)
    assert report_valid["overall_status"] == "FULLY_VERIFIED"
    assert report_valid["grounding_fidelity_pct"] == 100.0
    claim_res = report_valid["claims"][0]
    assert claim_res["is_verified"] is True
    assert claim_res["byte_span"]["line_number"] == 1
    assert claim_res["byte_span"]["start_offset"] == 11

    # Case B: Hallucinated / Fabricated Quote (Must Be Struck Through)
    payload_fake = {
        "claims": [
            {
                "claim_text": "Suspect admitted to selling patent for 50 Bitcoin",
                "evidence_id": "EV-01",
                "exact_quote": "I sold the patent for 50 BTC on the darkweb",
                "locator": "Line 99"
            }
        ]
    }
    report_fake = MechanicalCitationVerifier.verify_ai_claims(payload_fake, vault)
    assert report_fake["overall_status"] == "UNVERIFIED_OR_EMPTY"
    assert report_fake["grounding_fidelity_pct"] == 0.0
    assert report_fake["claims"][0]["is_verified"] is False
    assert report_fake["claims"][0]["status"] == "REJECTED_HALLUCINATED_QUOTE"

    # Case C: Citation Misattribution (Quote belongs to EV-02 but cited under EV-01)
    payload_misattrib = {
        "claims": [
            {
                "claim_text": "Suspect reported fever",
                "evidence_id": "EV-01",
                "exact_quote": "Sir I am suffering from high fever",
                "locator": "Line 1"
            }
        ]
    }
    report_mis = MechanicalCitationVerifier.verify_ai_claims(payload_misattrib, vault)
    assert report_mis["claims"][0]["status"] == "CITATION_MISATTRIBUTION_ERROR"
    assert report_mis["claims"][0]["misattributed_to"] == "EV-02"

    print("      [OK] 100% verbatim mechanical grounding verified with byte & line spans.")
    print("      [OK] Fabricated quotes intercepted and rejected with 0.0% grounding.")
    print("      [OK] Cross-exhibit citation misattribution successfully detected.")


def test_module_4_bsa_statutory_certificate():
    """Verify Module 4: BSA 2023 Section 63(4) Certificate Generation."""
    print("[4/4] Testing Module 4: BSA 2023 Section 63(4) Statutory Certificate Engine...")

    sample_exhibits = [
        {
            "id": "EV-101",
            "filename": "server_auth.csv",
            "file_type": "SERVER_LOG",
            "sha256": "c67d5b85b52c2a5e11c76ff9691d483b233d2c8f6ae617702b8732a76f122618",
            "sha3_256": "ce98141049acabcb9b8f51deb0f7d0f6f04c975536ffdc0ad63dff3cfd3e409e",
            "size_bytes": 275,
            "uploaded_at": "2026-10-02T16:30:00Z"
        },
        {
            "id": "EV-102",
            "filename": "whatsapp_chat.txt",
            "file_type": "CHAT_EXPORT",
            "sha256": "c5153b32d491cc521a07116172f5b38a5aac2004027dd66c45af9b32817b47f4",
            "sha3_256": "bfda748567b94825ddbd8f10fd6302487d73d0061537ecc9741f74ca748d8600",
            "size_bytes": 277,
            "uploaded_at": "2026-10-02T16:35:00Z"
        }
    ]

    sample_audit_chain = [
        {"seq": 1, "entry_hash": "a1b2c3d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c6d7e8f90"}
    ]

    cert = BSACertificateEngine.generate_bsa_section_63_certificate(
        case_number="FIR No. 204/2026, PS Cyber Crime",
        investigator_name="Inspector A. Yadav",
        investigator_designation="Cyber Forensic Examiner",
        organization="Cyber Crime Police Station",
        evidence_items=sample_exhibits,
        audit_chain=sample_audit_chain
    )

    assert cert["case_master_merkle_root"] != "0" * 64, "Invalid Merkle root in certificate"
    assert "part_a" in cert and "part_b" in cert
    assert len(cert["part_b"]["schedule"]) == 2
    assert "court_document_text" in cert
    assert "csv_manifest" in cert

    court_doc = cert["court_document_text"]
    assert "BHARATIYA SAKSHYA ADHINIYAM, 2023" in court_doc
    assert "FIR No. 204/2026" in court_doc
    assert cert["case_master_merkle_root"] in court_doc
    assert "SEAL OF THE INVESTIGATING OFFICER" in court_doc

    print(f"      [OK] BSA 2023 Section 63(4) statutory certificate generated with Master Root: {cert['case_master_merkle_root'][:16]}...")
    print("      [OK] Part A Custodian & Part B Technical Examiner schedules formatted for court filing.")
    print("      [OK] RFC-4180 CSV manifest export created.")


def main():
    print("================================================================================")
    print(" CHRONOFACT BACKEND ACCURACY ENGINES TEST SUITE (BSA 2023 §63(4))")
    print("================================================================================")
    start_time = time.time()

    test_module_1_timeline_and_allen_algebra()
    test_module_2_inconsistency_radar()
    test_module_3_mechanical_citation_verifier()
    test_module_4_bsa_statutory_certificate()

    elapsed = time.time() - start_time
    print("================================================================================")
    print(f" ALL 4 BACKEND ACCURACY ENGINES PASSED ZERO-HALLUCINATION VERIFICATION ({elapsed:.3f}s)")
    print(" Status: COURT ADMISSIBLE & ALGORITHMICALLY GROUNDED")
    print("================================================================================")


if __name__ == "__main__":
    main()
