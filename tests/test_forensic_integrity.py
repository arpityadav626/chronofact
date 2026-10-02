"""
CHRONOFACT Forensic Cryptographic Accuracy & Integrity Verification Test Suite
==============================================================================
Validates:
1. NIST FIPS 180-4 (SHA-256) & NIST FIPS 202 (SHA-3-256) accuracy against official test vectors.
2. 64KB streaming buffer chunk equivalence on multi-block payloads.
3. Read-only filesystem access timestamp (atime) strict preservation.
4. Deterministic Lexicographical Binary Merkle Tree calculation and proof verification.
5. End-to-end self-auditing `verify_case_integrity()` functionality.
6. Detection of 1-bit tampering raising uncatchable `ForensicIntegrityViolationError`.
"""

import os
import sys
import time
import tempfile
import sqlite3
import hashlib
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

from app.core.forensic_hasher import (
    ForensicHashEngine,
    MerkleTreeEngine,
    verify_case_integrity,
    ForensicIntegrityViolationError,
    ExhibitDigest,
    CHUNK_SIZE
)


def test_nist_hash_vectors():
    """Verify SHA-256 (FIPS 180-4) and SHA-3-256 (FIPS 202) against official NIST test vectors."""
    print("[1/6] Running NIST FIPS Cryptographic Test Vectors...")
    
    # NIST Test Vector 1: Empty string ""
    # SHA-256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
    # SHA-3-256: a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a
    digest_empty = ForensicHashEngine.compute_dual_hash_bytes(b"", evidence_id="TEST-EMPTY")
    assert digest_empty.sha256 == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", "Empty SHA-256 mismatch"
    assert digest_empty.sha3_256 == "a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a", "Empty SHA-3-256 mismatch"

    # NIST Test Vector 2: "abc"
    # SHA-256: ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad
    # SHA-3-256: 3a985da74fe225b2045c172d6bd390bd855f086e3e9d525b46bfe24511431532
    digest_abc = ForensicHashEngine.compute_dual_hash_bytes(b"abc", evidence_id="TEST-ABC")
    assert digest_abc.sha256 == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad", "'abc' SHA-256 mismatch"
    assert digest_abc.sha3_256 == "3a985da74fe225b2045c172d6bd390bd855f086e3e9d525b46bfe24511431532", "'abc' SHA-3-256 mismatch"

    print("      [OK] NIST FIPS 180-4 and FIPS 202 digests match official vectors 100%.")


def test_streaming_chunk_equivalence():
    """Verify that 64KB chunked streaming produces exact bit-for-bit identical hashes as in-memory hashing."""
    print("[2/6] Testing 64KB Chunk Streaming Equivalence on Multi-Block Payload...")
    
    # Generate 250 KB of non-trivial binary data spanning multiple 64KB chunks
    payload_size = 256 * 1024 + 17  # 262,161 bytes (> 4 full chunks)
    raw_data = os.urandom(payload_size)
    
    expected_sha256 = hashlib.sha256(raw_data).hexdigest().lower()
    expected_sha3_256 = hashlib.sha3_256(raw_data).hexdigest().lower()

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(raw_data)
        tmp_path = Path(tmp.name)

    try:
        digest = ForensicHashEngine.compute_dual_hash(tmp_path, evidence_id="TEST-STREAM")
        assert digest.sha256 == expected_sha256, "Streaming SHA-256 diverged from in-memory hash"
        assert digest.sha3_256 == expected_sha3_256, "Streaming SHA-3-256 diverged from in-memory hash"
        assert digest.size_bytes == payload_size, f"Size mismatch: {digest.size_bytes} != {payload_size}"
        print(f"      [OK] 64KB Streaming verified over {payload_size} bytes (Exact Dual Digest Match).")
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def test_access_timestamp_preservation():
    """Verify that hashing a physical exhibit preserves its access timestamp (ISO/IEC 27037)."""
    print("[3/6] Testing Access Timestamp (atime) Preservation...")
    
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b"Forensic Evidence Payload - Must Not Modify atime\n")
        tmp_path = Path(tmp.name)

    try:
        # Set an arbitrary past timestamp: 1 hour ago
        past_time = time.time() - 3600
        os.utime(tmp_path, (past_time, past_time))
        
        stat_before = tmp_path.stat()
        atime_before = stat_before.st_atime

        # Run dual-hash with preserve_timestamps=True
        digest = ForensicHashEngine.compute_dual_hash(tmp_path, preserve_timestamps=True)
        assert digest.atime_preserved, "atime_preserved flag reported False"

        stat_after = tmp_path.stat()
        atime_after = stat_after.st_atime

        # Assert atime is identical to before reading (within 1 second tolerance for coarse filesystems)
        assert abs(atime_after - atime_before) < 1.0, f"atime was altered! Before: {atime_before}, After: {atime_after}"
        print(f"      [OK] Original access timestamp preserved: {atime_before:.4f} == {atime_after:.4f}")
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def test_deterministic_merkle_tree():
    """Verify canonical sorting invariance and Merkle inclusion proofs."""
    print("[4/6] Testing Deterministic Lexicographical Merkle Tree Engine...")
    
    # 3 distinct test exhibit digests
    leaf_a = hashlib.sha256(b"Exhibit A - WhatsApp Chat").hexdigest().lower()
    leaf_b = hashlib.sha256(b"Exhibit B - Server Access Logs").hexdigest().lower()
    leaf_c = hashlib.sha256(b"Exhibit C - Corporate Email Archive").hexdigest().lower()

    # Ingestion order 1: [A, B, C]
    root_1 = MerkleTreeEngine.compute_case_merkle_root([leaf_a, leaf_b, leaf_c])
    
    # Ingestion order 2: [C, A, B] (Permutation)
    root_2 = MerkleTreeEngine.compute_case_merkle_root([leaf_c, leaf_a, leaf_b])

    # Ingestion order 3: [B, C, A] (Permutation)
    root_3 = MerkleTreeEngine.compute_case_merkle_root([leaf_b, leaf_c, leaf_a])

    # Must be 100% deterministic regardless of submission order
    assert root_1 == root_2 == root_3, f"Merkle Root is not order-invariant! {root_1} != {root_2}"
    print(f"      [OK] Order invariance confirmed: Master Merkle Root = {root_1}")

    # Test Merkle inclusion proof for leaf_b
    proof_result = MerkleTreeEngine.generate_inclusion_proof(leaf_b, [leaf_a, leaf_b, leaf_c])
    assert proof_result["verified"] is True, "Merkle inclusion proof verification failed"
    print(f"      [OK] Cryptographic inclusion proof verified for leaf {leaf_b[:12]}...")


def test_self_auditing_case_integrity():
    """Verify verify_case_integrity() on a pristine test case vault."""
    print("[5/6] Testing Self-Auditing verify_case_integrity() Function...")
    
    # Create isolated in-memory test database and temp vault
    with tempfile.TemporaryDirectory() as tmp_vault_dir:
        vault_path = Path(tmp_vault_dir)
        db_path = vault_path / "test_case.db"
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE evidence_items (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                file_type TEXT NOT NULL,
                sha256 TEXT NOT NULL,
                sha3_256 TEXT,
                size_bytes INTEGER NOT NULL,
                storage_path TEXT NOT NULL,
                source_description TEXT,
                uploaded_by TEXT,
                uploaded_at TEXT
            )
        """)

        # Ingest 2 physical test files
        file1 = vault_path / "EV-001_chat.txt"
        file1.write_bytes(b"WhatsApp Export: Suspect says I was sleeping at 11 PM.")
        digest1 = ForensicHashEngine.compute_dual_hash(file1, evidence_id="EV-001")

        file2 = vault_path / "EV-002_auth.csv"
        file2.write_bytes(b"2026-10-02T23:30:00Z,vikram.malhotra,192.168.1.105,LOGIN,OK")
        digest2 = ForensicHashEngine.compute_dual_hash(file2, evidence_id="EV-002")

        now_utc = "2026-10-02T23:45:00Z"
        cursor.execute("""
            INSERT INTO evidence_items VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("EV-001", "chat.txt", "CHAT_EXPORT", digest1.sha256, digest1.sha3_256, digest1.size_bytes, str(file1), "Chat Export", "IO Yadav", now_utc))

        cursor.execute("""
            INSERT INTO evidence_items VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("EV-002", "auth.csv", "SERVER_LOG", digest2.sha256, digest2.sha3_256, digest2.size_bytes, str(file2), "Server Log", "IO Yadav", now_utc))
        conn.commit()

        # Run verify_case_integrity
        report = verify_case_integrity(db_conn=conn)
        assert report["status"] == "CRYPTOGRAPHICALLY_INTACT"
        assert report["total_exhibits_audited"] == 2
        assert report["zero_bytes_altered"] is True
        assert report["total_bytes_verified"] == digest1.size_bytes + digest2.size_bytes
        print(f"      [OK] Audit passed: 2/2 physical files intact, Master Root: {report['case_merkle_root'][:16]}...")
        conn.close()


def test_tamper_detection_and_uncatchable_error():
    """Verify that altering 1 byte in physical storage raises ForensicIntegrityViolationError uncatchable by 'except Exception:'."""
    print("[6/6] Testing 1-Bit Tamper Detection & Uncatchable Exception Assertion...")
    
    with tempfile.TemporaryDirectory() as tmp_vault_dir:
        vault_path = Path(tmp_vault_dir)
        db_path = vault_path / "test_case.db"
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE evidence_items (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                file_type TEXT NOT NULL,
                sha256 TEXT NOT NULL,
                sha3_256 TEXT,
                size_bytes INTEGER NOT NULL,
                storage_path TEXT NOT NULL,
                source_description TEXT,
                uploaded_by TEXT,
                uploaded_at TEXT
            )
        """)

        file1 = vault_path / "EV-TAMPER_evidence.raw"
        file1.write_bytes(b"PRISTINE_ELECTRONIC_EVIDENCE_RECORD_FOR_COURT")
        digest1 = ForensicHashEngine.compute_dual_hash(file1, evidence_id="EV-TAMPER")

        cursor.execute("""
            INSERT INTO evidence_items VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("EV-TAMPER", "evidence.raw", "SERVER_LOG", digest1.sha256, digest1.sha3_256, digest1.size_bytes, str(file1), "Audit Test", "IO Yadav", "2026-10-02T23:50:00Z"))
        conn.commit()

        # --- SUBTLE TAMPERING: Flip exactly 1 character in the file ---
        # "PRISTINE" -> "XRISTINE" (1 byte difference)
        file1.write_bytes(b"XRISTINE_ELECTRONIC_EVIDENCE_RECORD_FOR_COURT")

        # CRITICAL TEST: Standard "except Exception:" MUST NOT catch ForensicIntegrityViolationError!
        tamper_detected_by_base_exception = False
        swallowed_by_generic_exception = False

        try:
            try:
                verify_case_integrity(db_conn=conn)
            except Exception as e:
                # If execution lands here, the error is CATCHABLE by generic Exception — THAT WOULD BE A FAILURE!
                swallowed_by_generic_exception = True
        except BaseException as fatal_exc:
            if isinstance(fatal_exc, ForensicIntegrityViolationError):
                tamper_detected_by_base_exception = True
                assert fatal_exc.evidence_id == "EV-TAMPER", "Incorrect evidence_id in exception"
                assert fatal_exc.expected_sha256 == digest1.sha256, "Incorrect expected_sha256"
                assert fatal_exc.actual_sha256 != digest1.sha256, "Actual hash should differ"
            else:
                raise fatal_exc

        assert not swallowed_by_generic_exception, "FAILURE: ForensicIntegrityViolationError was swallowed by generic 'except Exception:'!"
        assert tamper_detected_by_base_exception, "FAILURE: ForensicIntegrityViolationError was not raised or caught by BaseException handler!"

        print("      [OK] Tamper detected! 'ForensicIntegrityViolationError' successfully bypassed generic 'except Exception:' clauses.")
        print("      [OK] Forensic report payload verified with exact expected vs recalculated digests.")
        conn.close()


def main():
    print("================================================================================")
    print(" CHRONOFACT FORENSIC HASHING & INTEGRITY AUDIT TEST SUITE (BSA 2023 §63(4))")
    print("================================================================================")
    start_time = time.time()
    
    test_nist_hash_vectors()
    test_streaming_chunk_equivalence()
    test_access_timestamp_preservation()
    test_deterministic_merkle_tree()
    test_self_auditing_case_integrity()
    test_tamper_detection_and_uncatchable_error()

    elapsed = time.time() - start_time
    print("================================================================================")
    print(f" ALL 6 FORENSIC INTEGRITY & CRYPTOGRAPHIC TESTS PASSED ({elapsed:.3f}s)")
    print(" Status: LAW ENFORCEMENT & JUDICIAL INTEGRITY VALIDATED")
    print("================================================================================")


if __name__ == "__main__":
    main()
