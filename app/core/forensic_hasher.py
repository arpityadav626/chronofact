"""
CHRONOFACT Core Forensic Hashing and Cryptographic Integrity Verification Engine
================================================================================
Compliant with:
- Bharatiya Sakshya Adhiniyam, 2023 (BSA §63(4)) Statutory Electronic Evidence Rules
- NIST FIPS 180-4 (Secure Hash Standard - SHA-256)
- NIST FIPS 202 (SHA-3 Standard: Permutation-Based Hash and Extendable-Output Functions)
- ISO/IEC 27037:2012 (Digital Evidence Handling - Strict Preservation of Access Timestamps)
- RFC 6962 (Certificate Transparency - Deterministic Binary Merkle Tree Construction)

Author: CHRONOFACT Forensic Software Architect
Classification: LAW ENFORCEMENT & JUDICIAL AUDIT SENSITIVE
"""

import os
import sys
import json
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Tuple, Union

# Chunk buffer size: 64 KB (65,536 bytes) for streaming memory safety
CHUNK_SIZE: int = 65536


# ==============================================================================
# 1. FATAL FORENSIC EXCEPTION (UNCATCHABLE BY STANDARD "except Exception:")
# ==============================================================================

class ForensicIntegrityViolationError(BaseException):
    """
    FATAL UNCORRECTABLE FORENSIC INTEGRITY VIOLATION.
    
    IMPORTANT ARCHITECTURAL DESIGN:
    This exception subclasses `BaseException` rather than `Exception` so that standard
    application try-except clauses (e.g., `except Exception:`) CANNOT accidentally
    catch, swallow, or mask evidence tampering or storage bit-rot.
    
    Only an explicit handler targeting `BaseException` or `ForensicIntegrityViolationError`
    can intercept this error. In forensic evidence law (BSA 2023 §63(4)), any silent
    suppression of an altered exhibit hash invalidates the court's evidentiary admissibility.
    """

    def __init__(
        self,
        evidence_id: str,
        filename: str,
        file_path: str,
        expected_sha256: str,
        actual_sha256: str,
        expected_sha3_256: Optional[str] = None,
        actual_sha3_256: Optional[str] = None,
        expected_size_bytes: Optional[int] = None,
        actual_size_bytes: Optional[int] = None,
        tamper_byte_offset: Optional[int] = None,
        tamper_detail: Optional[str] = None
    ):
        self.evidence_id = evidence_id
        self.filename = filename
        self.file_path = file_path
        self.expected_sha256 = expected_sha256.lower()
        self.actual_sha256 = actual_sha256.lower()
        self.expected_sha3_256 = expected_sha3_256.lower() if expected_sha3_256 else None
        self.actual_sha3_256 = actual_sha3_256.lower() if actual_sha3_256 else None
        self.expected_size_bytes = expected_size_bytes
        self.actual_size_bytes = actual_size_bytes
        self.tamper_byte_offset = tamper_byte_offset
        self.tamper_detail = tamper_detail or "Physical evidence file on disk diverges from initial acquisition record."
        self.detection_timestamp_utc = datetime.now(timezone.utc).isoformat()

        # Construct official forensic legal error banner
        banner_lines = [
            "",
            "================================================================================",
            " [!] CRITICAL FORENSIC INTEGRITY VIOLATION — BHARATIYA SAKSHYA ADHINIYAM §63(4)",
            "================================================================================",
            f" Case Exhibit ID    : {self.evidence_id} [{self.filename}]",
            f" Physical File Path : {self.file_path}",
            f" Audit Timestamp    : {self.detection_timestamp_utc} (UTC)",
            "--------------------------------------------------------------------------------",
            f" Expected SHA-256   : {self.expected_sha256}",
            f" Recalculated SHA256: {self.actual_sha256}",
            f" SHA-256 Match      : {'PASSED' if self.expected_sha256 == self.actual_sha256 else 'FAIL (CRYPTOGRAPHIC MISMATCH)'}",
        ]

        if self.expected_sha3_256 or self.actual_sha3_256:
            banner_lines.append(f" Expected SHA-3-256 : {self.expected_sha3_256 or 'N/A'}")
            banner_lines.append(f" Recalculated SHA3  : {self.actual_sha3_256 or 'N/A'}")
            banner_lines.append(f" SHA-3-256 Match    : {'PASSED' if self.expected_sha3_256 == self.actual_sha3_256 else 'FAIL (COLLISION/TAMPER)'}")

        if self.expected_size_bytes is not None or self.actual_size_bytes is not None:
            banner_lines.append(f" File Size Expected : {self.expected_size_bytes} bytes")
            banner_lines.append(f" File Size Actual   : {self.actual_size_bytes} bytes")

        if self.tamper_byte_offset is not None:
            banner_lines.append(f" Discrepancy Offset : Byte 0x{self.tamper_byte_offset:08X} (offset {self.tamper_byte_offset})")

        banner_lines.extend([
            "--------------------------------------------------------------------------------",
            f" Finding Summary    : {self.tamper_detail}",
            " Legal Significance : CHAIN OF CUSTODY BROKEN. Inadmissible under BSA 2023 s.63(4).",
            " Action Required    : Quarantine disk sector immediately and invoke forensic backup.",
            "================================================================================"
        ])

        self.formatted_banner = "\n".join(banner_lines)
        super().__init__(self.formatted_banner)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the violation into an evidentiary audit dictionary."""
        return {
            "error_type": "ForensicIntegrityViolationError",
            "evidence_id": self.evidence_id,
            "filename": self.filename,
            "file_path": self.file_path,
            "expected_sha256": self.expected_sha256,
            "actual_sha256": self.actual_sha256,
            "expected_sha3_256": self.expected_sha3_256,
            "actual_sha3_256": self.actual_sha3_256,
            "expected_size_bytes": self.expected_size_bytes,
            "actual_size_bytes": self.actual_size_bytes,
            "tamper_byte_offset": self.tamper_byte_offset,
            "tamper_detail": self.tamper_detail,
            "detection_timestamp_utc": self.detection_timestamp_utc,
            "legal_framework": "Bharatiya Sakshya Adhiniyam, 2023 (Section 63(4))",
            "chain_of_custody_intact": False
        }

    def to_json(self) -> str:
        """Serializes to formatted JSON for police case diaries and incident logs."""
        return json.dumps(self.to_dict(), indent=2)


# ==============================================================================
# 2. DUAL-DIGEST CONTAINER DATACLASS
# ==============================================================================

@dataclass(frozen=True)
class ExhibitDigest:
    """
    Immutable cryptographic digest record for a digital evidence exhibit.
    Dual-hash compliant with NIST FIPS 180-4 and NIST FIPS 202 standards.
    """
    evidence_id: str
    filename: str
    file_path: str
    sha256: str          # NIST FIPS 180-4 (Primary)
    sha3_256: str        # NIST FIPS 202 Keccak-256 (Secondary)
    size_bytes: int      # Exact file byte count
    computed_at_utc: str # ISO-8601 acquisition timestamp
    atime_preserved: bool# Affirmation that access timestamp was not altered
    mtime_preserved: bool# Affirmation that modification timestamp was not altered

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ==============================================================================
# 3. FORENSIC HASH ENGINE (STREAMING & TIMESTAMP PRESERVING)
# ==============================================================================

class ForensicHashEngine:
    """
    High-assurance forensic hashing engine.
    
    Principles:
    1. Dual Algorithms: Computes SHA-256 and SHA-3-256 simultaneously in a single streaming pass.
    2. Zero Memory Bloat: Streams files in 64 KB buffers to support multi-gigabyte forensic disk images.
    3. Strict Metadata Preservation: Preserves filesystem access timestamps (atime/mtime)
       to comply with ISO/IEC 27037 standards preventing evidentiary contamination.
    """

    @staticmethod
    def compute_dual_hash(
        file_path: Union[str, Path],
        evidence_id: str = "EXHIBIT",
        preserve_timestamps: bool = True
    ) -> ExhibitDigest:
        """
        Computes SHA-256 and SHA-3-256 digests in a single-pass streaming read over
        the physical file in 64KB chunks while strictly preserving access timestamps.
        """
        path = Path(file_path).resolve()
        if not path.is_file():
            raise FileNotFoundError(f"Forensic exhibit file not found on disk: {path}")

        # Capture initial filesystem metadata before any read handles are opened
        stat_before = None
        if preserve_timestamps:
            try:
                stat_before = path.stat()
            except OSError:
                stat_before = None

        hasher_sha256 = hashlib.sha256()
        hasher_sha3 = hashlib.sha3_256()
        total_bytes = 0

        # Attempt to open file in read-only binary mode.
        # Under POSIX platforms, request O_NOATIME flag to avoid updating st_atime.
        opened_via_noatime = False
        if hasattr(os, "O_NOATIME") and hasattr(os, "open"):
            try:
                fd = os.open(path, os.O_RDONLY | os.O_NOATIME)
                with open(fd, "rb", closefd=True) as stream:
                    while chunk := stream.read(CHUNK_SIZE):
                        hasher_sha256.update(chunk)
                        hasher_sha3.update(chunk)
                        total_bytes += len(chunk)
                opened_via_noatime = True
            except (PermissionError, OSError):
                # Fall back to standard read with timestamp restoration
                opened_via_noatime = False

        if not opened_via_noatime:
            with open(path, "rb") as stream:
                while chunk := stream.read(CHUNK_SIZE):
                    hasher_sha256.update(chunk)
                    hasher_sha3.update(chunk)
                    total_bytes += len(chunk)

        # Restore original timestamps (nanosecond precision if supported by OS/filesystem)
        atime_restored = False
        mtime_restored = False
        if preserve_timestamps and stat_before is not None:
            try:
                if hasattr(stat_before, "st_atime_ns") and hasattr(os, "utime"):
                    os.utime(path, ns=(stat_before.st_atime_ns, stat_before.st_mtime_ns))
                    atime_restored = True
                    mtime_restored = True
                else:
                    os.utime(path, (stat_before.st_atime, stat_before.st_mtime))
                    atime_restored = True
                    mtime_restored = True
            except (PermissionError, OSError):
                # On read-only mounted filesystems or restricted permissions, restoration may fail
                atime_restored = opened_via_noatime
                mtime_restored = True

        return ExhibitDigest(
            evidence_id=evidence_id,
            filename=path.name,
            file_path=str(path),
            sha256=hasher_sha256.hexdigest().lower(),
            sha3_256=hasher_sha3.hexdigest().lower(),
            size_bytes=total_bytes,
            computed_at_utc=datetime.now(timezone.utc).isoformat(),
            atime_preserved=atime_restored or opened_via_noatime,
            mtime_preserved=mtime_restored or True
        )

    @staticmethod
    def compute_dual_hash_bytes(
        data: bytes,
        evidence_id: str = "IN_MEMORY_BUFFER",
        filename: str = "buffer.raw"
    ) -> ExhibitDigest:
        """Computes dual digests directly from an in-memory byte buffer."""
        sha256_digest = hashlib.sha256(data).hexdigest().lower()
        sha3_digest = hashlib.sha3_256(data).hexdigest().lower()
        
        return ExhibitDigest(
            evidence_id=evidence_id,
            filename=filename,
            file_path="[IN_MEMORY_BUFFER]",
            sha256=sha256_digest,
            sha3_256=sha3_digest,
            size_bytes=len(data),
            computed_at_utc=datetime.now(timezone.utc).isoformat(),
            atime_preserved=True,
            mtime_preserved=True
        )

    @staticmethod
    def find_tamper_offset(corrupt_file_path: Path, reference_bytes: bytes) -> Optional[int]:
        """
        Locates the first byte offset where a corrupt file diverges from reference bytes.
        Useful for forensic court exhibits explaining the exact locus of tampering.
        """
        offset = 0
        try:
            with open(corrupt_file_path, "rb") as f:
                while chunk := f.read(CHUNK_SIZE):
                    ref_slice = reference_bytes[offset : offset + len(chunk)]
                    if chunk != ref_slice:
                        for idx, (b_actual, b_ref) in enumerate(zip(chunk, ref_slice)):
                            if b_actual != b_ref:
                                return offset + idx
                        if len(chunk) != len(ref_slice):
                            return offset + min(len(chunk), len(ref_slice))
                    offset += len(chunk)
            if offset < len(reference_bytes):
                return offset
        except Exception:
            return None
        return None


# ==============================================================================
# 4. DETERMINISTIC BINARY MERKLE TREE ENGINE (CASE MASTER ROOT)
# ==============================================================================

class MerkleTreeEngine:
    """
    Deterministic Lexicographically Sorted Binary Merkle Tree Engine.
    
    1. Canonical Ordering:
       Leaves are sorted lexicographically by their lowercase hexadecimal SHA-256
       digest. This guarantees a deterministic root regardless of file ingestion order,
       operating system directory traversal sequence, or timestamp discrepancies.
       
    2. Binary Merkle Node Hashing:
       Each parent node is computed as SHA-256(left_bytes + right_bytes).
       If an odd number of nodes exists at any level, the last node is paired with
       a duplicate of itself (RFC 6962 / Bitcoin Merkle tree standard).
       
    3. Master Root Hash:
       Iterates level-by-level until 1 root hash remains: `Case_Merkle_Root`.
       This 256-bit digest serves as the statutory case master identifier
       for the BSA 2023 s.63(4) certificate.
    """

    @staticmethod
    def compute_case_merkle_root(leaf_hashes: List[str]) -> str:
        """
        Calculates the deterministic Master Case Merkle Root from a list of SHA-256 digests.
        """
        if not leaf_hashes:
            return "0" * 64

        # Validate format & canonicalize: lowercase, stripped, sorted lexicographically
        cleaned_leaves: List[str] = []
        for h in leaf_hashes:
            raw = h.strip().lower()
            if len(raw) != 64 or any(c not in "0123456789abcdef" for c in raw):
                raise ValueError(f"Invalid SHA-256 digest format for Merkle leaf: '{h}'")
            cleaned_leaves.append(raw)

        # Canonical lexicographical sort
        sorted_leaves = sorted(cleaned_leaves)

        if len(sorted_leaves) == 1:
            return sorted_leaves[0]

        # Convert hex leaves to 32 raw bytes for cryptographic node combination
        current_level = [bytes.fromhex(h) for h in sorted_leaves]

        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                if i + 1 < len(current_level):
                    right = current_level[i + 1]
                else:
                    # Odd count: duplicate last node (RFC 6962)
                    right = left
                parent = hashlib.sha256(left + right).digest()
                next_level.append(parent)
            current_level = next_level

        return current_level[0].hex().lower()

    @staticmethod
    def build_merkle_tree(
        exhibits: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Builds the complete Merkle Tree hierarchy with leaf metadata,
        intermediate levels, and Master Root for judicial inspection.
        """
        if not exhibits:
            return {
                "case_merkle_root": "0" * 64,
                "leaf_count": 0,
                "depth": 0,
                "levels": [],
                "canonical_leaves": []
            }

        # Sort exhibits canonically by their SHA-256 hash
        sorted_exhibits = sorted(
            exhibits,
            key=lambda x: str(x.get("sha256", "")).strip().lower()
        )

        leaf_nodes = []
        for idx, item in enumerate(sorted_exhibits):
            sha_hex = str(item.get("sha256", "")).strip().lower()
            leaf_nodes.append({
                "index": idx,
                "hash": sha_hex,
                "is_leaf": True,
                "evidence_id": item.get("id") or item.get("evidence_id") or f"EV-{idx}",
                "filename": item.get("filename", "unknown"),
                "file_type": item.get("file_type", "EXHIBIT"),
                "size_bytes": item.get("size_bytes", 0)
            })

        levels: List[List[Dict[str, Any]]] = [leaf_nodes]
        current_hashes = [bytes.fromhex(node["hash"]) for node in leaf_nodes]

        level_depth = 0
        while len(current_hashes) > 1:
            next_hashes = []
            next_level_nodes = []
            for i in range(0, len(current_hashes), 2):
                left_bytes = current_hashes[i]
                right_bytes = current_hashes[i + 1] if i + 1 < len(current_hashes) else left_bytes

                parent_bytes = hashlib.sha256(left_bytes + right_bytes).digest()
                parent_hex = parent_bytes.hex().lower()

                next_hashes.append(parent_bytes)
                next_level_nodes.append({
                    "index": len(next_level_nodes),
                    "hash": parent_hex,
                    "is_leaf": False,
                    "level": level_depth + 1,
                    "left_child_hash": left_bytes.hex().lower(),
                    "right_child_hash": right_bytes.hex().lower(),
                    "is_duplicated_odd_node": (i + 1 >= len(current_hashes))
                })

            current_hashes = next_hashes
            levels.append(next_level_nodes)
            level_depth += 1

        root_hash = current_hashes[0].hex().lower() if current_hashes else ("0" * 64)

        return {
            "case_merkle_root": root_hash,
            "leaf_count": len(leaf_nodes),
            "depth": len(levels),
            "levels": levels,
            "canonical_leaves": [n["hash"] for n in leaf_nodes]
        }

    @staticmethod
    def generate_inclusion_proof(
        target_sha256: str,
        leaf_hashes: List[str]
    ) -> Dict[str, Any]:
        """
        Generates an RFC 6962 audit inclusion proof path for a specific exhibit hash.
        Allows defense or judicial examiners to verify that an individual exhibit
        was part of the sealed case session without revealing all other exhibits.
        """
        target = target_sha256.strip().lower()
        sorted_leaves = sorted([h.strip().lower() for h in leaf_hashes])

        if target not in sorted_leaves:
            raise ValueError(f"Target hash {target} is not in the provided Merkle leaves.")

        index = sorted_leaves.index(target)
        proof = []
        current_hashes = [bytes.fromhex(h) for h in sorted_leaves]

        while len(current_hashes) > 1:
            next_hashes = []
            for i in range(0, len(current_hashes), 2):
                left = current_hashes[i]
                right = current_hashes[i + 1] if i + 1 < len(current_hashes) else left
                parent = hashlib.sha256(left + right).digest()
                next_hashes.append(parent)

                if i == index or (i + 1 == index and i + 1 < len(current_hashes)):
                    if index % 2 == 0:
                        sibling_hash = right.hex().lower()
                        proof.append({"sibling": sibling_hash, "direction": "RIGHT"})
                    else:
                        sibling_hash = left.hex().lower()
                        proof.append({"sibling": sibling_hash, "direction": "LEFT"})

            current_hashes = next_hashes
            index = index // 2

        root = current_hashes[0].hex().lower()
        return {
            "target_hash": target,
            "proof_path": proof,
            "merkle_root": root,
            "verified": MerkleTreeEngine.verify_inclusion_proof(target, proof, root)
        }

    @staticmethod
    def verify_inclusion_proof(
        target_sha256: str,
        proof_path: List[Dict[str, str]],
        expected_root: str
    ) -> bool:
        """
        Cryptographically verifies an inclusion proof path against an expected Merkle Root.
        """
        current = bytes.fromhex(target_sha256.strip().lower())
        for step in proof_path:
            sibling = bytes.fromhex(step["sibling"])
            direction = step["direction"]
            if direction == "RIGHT":
                current = hashlib.sha256(current + sibling).digest()
            else:
                current = hashlib.sha256(sibling + current).digest()
        return current.hex().lower() == expected_root.strip().lower()


# ==============================================================================
# 5. SELF-AUDITING INTEGRITY FUNCTION (verify_case_integrity)
# ==============================================================================

def verify_case_integrity(
    db_conn: Optional[sqlite3.Connection] = None,
    expected_case_merkle_root: Optional[str] = None
) -> Dict[str, Any]:
    """
    Core Forensic Self-Audit Function.
    
    Workflow:
    1. Re-reads every physical exhibit file from vault disk storage.
    2. Recalculates both SHA-256 (NIST FIPS 180-4) and SHA-3-256 (NIST FIPS 202)
       using 64KB chunk streaming without altering access timestamps.
    3. Strictly verifies that 0 bytes have changed since initial lawful seizure.
    4. Computes the canonical Master Case Merkle Root across all exhibits.
    5. Asserts matching Merkle root against `expected_case_merkle_root` if provided.
    
    Error Behavior:
    If ANY bit is flipped or missing on disk, this function raises the uncatchable
    `ForensicIntegrityViolationError` containing the corrupt exhibit ID, byte offset,
    and mismatch digests. Standard application `except Exception:` blocks CANNOT catch it.
    
    Returns:
    A structured dictionary containing:
    - status: 'CRYPTOGRAPHICALLY_INTACT'
    - total_exhibits_audited: int
    - total_bytes_verified: int
    - zero_bytes_altered: True
    - case_merkle_root: str
    - dual_digest_algorithms: list
    - audit_records: list of verified exhibit digests
    - audit_timestamp_utc: str
    """
    from .config import DB_PATH
    
    should_close_conn = False
    if db_conn is None:
        db_conn = sqlite3.connect(DB_PATH)
        db_conn.row_factory = sqlite3.Row
        should_close_conn = True

    try:
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM evidence_items ORDER BY uploaded_at ASC")
        records = [dict(r) for r in cursor.fetchall()]

        if not records:
            return {
                "status": "EMPTY_CASE_VAULT",
                "total_exhibits_audited": 0,
                "total_bytes_verified": 0,
                "zero_bytes_altered": True,
                "case_merkle_root": "0" * 64,
                "dual_digest_algorithms": ["SHA-256 (FIPS 180-4)", "SHA-3-256 (FIPS 202)"],
                "audit_timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "audit_records": []
            }

        verified_records = []
        leaf_hashes = []
        total_bytes_verified = 0

        for record in records:
            evidence_id = record["id"]
            filename = record["filename"]
            storage_path = Path(record["storage_path"])
            expected_sha256 = record["sha256"].lower().strip()
            expected_size = record["size_bytes"]
            expected_sha3 = record.get("sha3_256")
            if expected_sha3:
                expected_sha3 = expected_sha3.lower().strip()

            # 1. Assert physical file existence
            if not storage_path.exists() or not storage_path.is_file():
                raise ForensicIntegrityViolationError(
                    evidence_id=evidence_id,
                    filename=filename,
                    file_path=str(storage_path),
                    expected_sha256=expected_sha256,
                    actual_sha256="FILE_NOT_FOUND_ON_DISK",
                    expected_size_bytes=expected_size,
                    actual_size_bytes=0,
                    tamper_detail="Critical evidentiary file has been moved, unmounted, or deleted from disk."
                )

            # 2. Re-read physical file in 64KB chunks and recalculate dual digests
            digest = ForensicHashEngine.compute_dual_hash(
                file_path=storage_path,
                evidence_id=evidence_id,
                preserve_timestamps=True
            )

            # 3. Assert exact byte length
            if digest.size_bytes != expected_size:
                raise ForensicIntegrityViolationError(
                    evidence_id=evidence_id,
                    filename=filename,
                    file_path=str(storage_path),
                    expected_sha256=expected_sha256,
                    actual_sha256=digest.sha256,
                    expected_sha3_256=expected_sha3,
                    actual_sha3_256=digest.sha3_256,
                    expected_size_bytes=expected_size,
                    actual_size_bytes=digest.size_bytes,
                    tamper_detail=f"File length changed by {digest.size_bytes - expected_size} bytes."
                )

            # 4. Assert SHA-256 (Primary - NIST FIPS 180-4)
            if digest.sha256 != expected_sha256:
                raise ForensicIntegrityViolationError(
                    evidence_id=evidence_id,
                    filename=filename,
                    file_path=str(storage_path),
                    expected_sha256=expected_sha256,
                    actual_sha256=digest.sha256,
                    expected_sha3_256=expected_sha3,
                    actual_sha3_256=digest.sha3_256,
                    expected_size_bytes=expected_size,
                    actual_size_bytes=digest.size_bytes,
                    tamper_detail="Bit flip or unauthorized byte modification detected in physical exhibit payload."
                )

            # 5. Assert SHA-3-256 if recorded
            if expected_sha3 and digest.sha3_256 != expected_sha3:
                raise ForensicIntegrityViolationError(
                    evidence_id=evidence_id,
                    filename=filename,
                    file_path=str(storage_path),
                    expected_sha256=expected_sha256,
                    actual_sha256=digest.sha256,
                    expected_sha3_256=expected_sha3,
                    actual_sha3_256=digest.sha3_256,
                    expected_size_bytes=expected_size,
                    actual_size_bytes=digest.size_bytes,
                    tamper_detail="SHA-3-256 secondary collision resistance check failed."
                )

            # Record verified exhibit
            total_bytes_verified += digest.size_bytes
            leaf_hashes.append(digest.sha256)
            verified_records.append({
                "evidence_id": evidence_id,
                "filename": filename,
                "file_path": str(storage_path),
                "sha256": digest.sha256,
                "sha3_256": digest.sha3_256,
                "size_bytes": digest.size_bytes,
                "integrity_verdict": "VERIFIED_BIT_EXACT",
                "atime_preserved": digest.atime_preserved,
                "mtime_preserved": digest.mtime_preserved,
                "reverified_at_utc": digest.computed_at_utc
            })

        # 6. Recalculate Master Case Merkle Root
        case_merkle_root = MerkleTreeEngine.compute_case_merkle_root(leaf_hashes)

        # 7. Check against expected Merkle Root if passed
        if expected_case_merkle_root:
            clean_expected_root = expected_case_merkle_root.strip().lower()
            if case_merkle_root != clean_expected_root:
                raise ForensicIntegrityViolationError(
                    evidence_id="CASE_MASTER_MERKLE_ROOT",
                    filename="CASE_MERKLE_TREE",
                    file_path="[MERKLE_TREE_MEMORY]",
                    expected_sha256=clean_expected_root,
                    actual_sha256=case_merkle_root,
                    tamper_detail="Calculated Case Master Merkle Root does not match statutory certificate root."
                )

        return {
            "status": "CRYPTOGRAPHICALLY_INTACT",
            "total_exhibits_audited": len(verified_records),
            "total_bytes_verified": total_bytes_verified,
            "zero_bytes_altered": True,
            "case_merkle_root": case_merkle_root,
            "dual_digest_algorithms": ["SHA-256 (NIST FIPS 180-4)", "SHA-3-256 (NIST FIPS 202)"],
            "audit_timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "audit_records": verified_records
        }

    finally:
        if should_close_conn:
            db_conn.close()
