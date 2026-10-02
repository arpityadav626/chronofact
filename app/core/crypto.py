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
