"""Regression tests for the v2 fixes. Pure Python: no FastAPI needed."""
import hashlib, random, sqlite3, time
from datetime import timezone
from pathlib import Path
import pytest

from app.core.safety import build_fts_query, resolve_inside, sanitize_filename
from app.core import auth
from app.core.forensic_hasher import MerkleTreeEngine as M
from app.core.crypto import HashChainedAuditLogger, verify_audit_chain
from app.engines.inconsistency import chat_reference_instant, detect_inconsistencies

H = lambda s: hashlib.sha256(s.encode()).hexdigest()


def test_sanitize_filename():
    assert sanitize_filename("../../etc/passwd") == "passwd"
    assert sanitize_filename("C:\\Windows\\x.csv") == "x.csv"
    assert sanitize_filename("CON.txt") == "_CON.txt"
    assert sanitize_filename("") == "unnamed_exhibit.bin"
    assert "/" not in sanitize_filename("a/b\\c.txt")
    assert len(sanitize_filename("a" * 500 + ".csv")) <= 120


def test_resolve_inside(tmp_path):
    assert resolve_inside(tmp_path, "ok.txt").parent == tmp_path.resolve()
    with pytest.raises(ValueError):
        resolve_inside(tmp_path, "../escape.txt")


def test_fts_query_is_neutral():
    q = build_fts_query('foo AND "bar" NEAR(x) col:evil* 192.168.1.105')
    assert q.count('"') % 2 == 0 and '"192.168.1.105"' in q
    assert build_fts_query("a b") is None


def test_password_hash_and_tokens():
    h = auth.get_password_hash("s3cret-pass-phrase")
    assert h.startswith("scrypt$") and auth.verify_password("s3cret-pass-phrase", h)
    assert not auth.verify_password("wrong", h) and not auth.verify_password("x", "garbage")
    tok = auth.create_access_token({"sub": "lead", "role": "examiner"})
    assert auth.user_from_token(tok)["username"] == "lead"
    assert auth.user_from_token(tok + "x") is None
    assert auth.authenticate_user("examiner", "SecurePassMin16Chars!") is None  # no baked-in demo account


def test_login_throttle():
    t = auth.LoginThrottle(max_failures=3, lock_seconds=60)
    for _ in range(3):
        t.record_failure("1.1.1.1", "u")
    assert t.seconds_locked("1.1.1.1", "u") > 0 and t.seconds_locked("2.2.2.2", "u") == 0
    t.record_success("1.1.1.1", "u")
    assert t.seconds_locked("1.1.1.1", "u") == 0


@pytest.mark.parametrize("n", range(1, 18))
def test_merkle_proofs_all_sizes(n):
    leaves = [H(f"x{i}") for i in range(n)]
    root = M.compute_case_merkle_root(leaves)
    random.shuffle(leaves)
    assert M.compute_case_merkle_root(leaves) == root
    for l in leaves:
        pr = M.generate_inclusion_proof(l, leaves)
        assert pr["verified"] and pr["merkle_root"] == root
        assert not M.verify_inclusion_proof(H("evil"), pr["proof_path"], root)


def test_merkle_second_preimage_and_duplicate_ambiguity():
    a, b, c = H("a"), H("b"), H("c")
    two = M.compute_case_merkle_root([a, b])
    fake_leaf = hashlib.sha256(b"\x01" + M.hash_leaf(a) + M.hash_leaf(b)).hexdigest()
    assert M.compute_case_merkle_root([fake_leaf]) != two
    assert M.compute_case_merkle_root([a, b, c]) != M.compute_case_merkle_root([a, b, c, c])
    assert M.compute_case_merkle_root([a]) != a  # single leaf is domain-separated too


def test_audit_chain_detects_forgery():
    rows, prev = [], "0" * 64
    for i in range(1, 5):
        e = HashChainedAuditLogger.create_log_entry(i, "u", "ACT", f"T{i}", "0" * 64, prev, {"i": i})
        rows.append(e); prev = e["entry_hash"]
    assert verify_audit_chain(rows)["status"] == "CHAIN_INTACT"
    rows[2] = dict(rows[2], actor="forged")
    assert verify_audit_chain(rows)["status"] == "CHAIN_BROKEN"


def test_alibi_rule_uses_assumed_zone_and_is_forward_looking():
    chat = {"id": "C1", "fact_type": "CHAT_MESSAGE", "locator": "L1", "tz_basis": "assumed_local_no_offset",
            "raw_text": "[12/09/2025, 15:25:40] V: I am asleep, offline till morning",
            "t_min": "2025-09-12T01:25:40+00:00", "t_max": "2025-09-13T03:25:40+00:00"}
    assert chat_reference_instant(chat).isoformat() == "2025-09-12T09:55:40+00:00"  # 15:25:40 IST
    def log(i, ts, act):
        return {"id": i, "fact_type": "SERVER_LOG_EVENT", "locator": i, "actor": "v", "t_min": ts, "t_max": ts,
                "tz_basis": "x", "time_reliability": "x", "raw_text": f"{ts},v,10.0.0.1,{act},OK"}
    before = log("L0", "2025-09-12T09:54:10+00:00", "LOGIN")         # 90 s BEFORE the claim: not a contradiction
    after = log("L1", "2025-09-12T09:58:45+00:00", "DOWNLOAD_FILE")  # 3 min after: contradiction
    hits = [i for i in detect_inconsistencies([chat, before, after], []) if i["rule_id"] == "RULE_ALIBI_VS_SERVER_LOG"]
    assert len(hits) == 1 and hits[0]["fact_ids"][1] == "L1" and "timezone_assumption" in hits[0]
    assert not [i for i in detect_inconsistencies([chat, before], []) if i["rule_id"] == "RULE_ALIBI_VS_SERVER_LOG"]
