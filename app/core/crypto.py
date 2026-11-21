import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, Union

# Re-export core forensic modules
from .forensic_hasher import (
    ForensicIntegrityViolationError,
    ExhibitDigest,
    ForensicHashEngine,
    MerkleTreeEngine,
    verify_case_integrity,
    CHUNK_SIZE
)

def compute_sha256_file(file_path: Union[str, Path]) -> str:
    """
    Computes SHA-256 digest of a given file in 64KB chunks while preserving access timestamps.
    Delegates to ForensicHashEngine for strict forensic compliance.
    """
    return ForensicHashEngine.compute_dual_hash(file_path, preserve_timestamps=True).sha256

def compute_dual_hash_file(file_path: Union[str, Path]) -> ExhibitDigest:
    """Computes both SHA-256 and SHA-3-256 digests in a streaming pass."""
    return ForensicHashEngine.compute_dual_hash(file_path, preserve_timestamps=True)

def compute_sha256_text(text: str) -> str:
    """Computes SHA-256 digest of a string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def compute_case_merkle_root(leaf_hashes: list) -> str:
    """Computes deterministic Master Case Merkle Root."""
    return MerkleTreeEngine.compute_case_merkle_root(leaf_hashes)

class HashChainedAuditLogger:
    """
    Tamper-Evident Hash Chain:
    Entry_k = SHA-256(Index + Timestamp + Actor + Action + TargetHash + PrevHash)
    Any retrospective alteration of previous log entries invalidates the entire chain.
    """
    @staticmethod
    def create_log_entry(
        seq: int,
        actor: str,
        action: str,
        target_id: str,
        target_hash: str,
        prev_hash: str,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        timestamp = datetime.now(timezone.utc).isoformat()
        details_str = json.dumps(details or {}, sort_keys=True)
        
        # Canonical string for cryptographic chaining
        payload = f"{seq}|{timestamp}|{actor}|{action}|{target_id}|{target_hash}|{details_str}|{prev_hash}"
        entry_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        
        return {
            "seq": seq,
            "timestamp": timestamp,
            "actor": actor,
            "action": action,
            "target_id": target_id,
            "target_hash": target_hash,
            "details": details_str,
            "prev_hash": prev_hash,
            "entry_hash": entry_hash
        }


def append_audit_entry(cursor, actor: str, action: str, target_id: str, target_hash: str,
                       details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Append one entry to the hash-chained audit log using the caller's open transaction.
    The caller must hold a write lock (BEGIN IMMEDIATE) so two concurrent requests cannot
    both read the same previous entry and fork the chain.
    """
    cursor.execute("SELECT seq, entry_hash FROM audit_log ORDER BY seq DESC LIMIT 1")
    last = cursor.fetchone()
    prev_seq = last["seq"] if last else 0
    prev_hash = last["entry_hash"] if last else "0" * 64
    entry = HashChainedAuditLogger.create_log_entry(
        seq=prev_seq + 1, actor=actor, action=action, target_id=target_id,
        target_hash=target_hash, prev_hash=prev_hash, details=details,
    )
    cursor.execute(
        """INSERT INTO audit_log (seq, timestamp, actor, action, target_id, target_hash, details, prev_hash, entry_hash)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (entry["seq"], entry["timestamp"], entry["actor"], entry["action"], entry["target_id"],
         entry["target_hash"], entry["details"], entry["prev_hash"], entry["entry_hash"]),
    )
    return entry


def verify_audit_chain(rows: list) -> Dict[str, Any]:
    """
    Recompute every entry hash and check prev_hash linkage.
    `rows` = audit_log rows (dict-like) ordered by seq ASC.
    A pre-v2 genesis row (whose entry_hash was stored as the number 0) is accepted as the anchor.
    """
    problems = []
    prev_hash = None
    for idx, r in enumerate(rows):
        r = dict(r)
        payload = "|".join(str(r[k]) for k in ("seq", "timestamp", "actor", "action", "target_id", "target_hash")) \
                  + f"|{r['details']}|{r['prev_hash']}"
        recomputed = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        legacy_genesis = (idx == 0 and r["action"] == "GENESIS_INIT" and str(r["entry_hash"]) in ("0", "0" * 64))
        if not legacy_genesis and recomputed != r["entry_hash"]:
            problems.append({"seq": r["seq"], "issue": "ENTRY_HASH_MISMATCH"})
        if prev_hash is not None and r["prev_hash"] != prev_hash:
            problems.append({"seq": r["seq"], "issue": "BROKEN_PREV_LINK"})
        if idx > 0 and r["seq"] != rows[idx - 1]["seq"] + 1:
            problems.append({"seq": r["seq"], "issue": "SEQUENCE_GAP"})
        prev_hash = r["entry_hash"]
    return {
        "status": "CHAIN_INTACT" if not problems else "CHAIN_BROKEN",
        "entries_checked": len(rows),
        "head_hash": prev_hash,
        "problems": problems,
    }
