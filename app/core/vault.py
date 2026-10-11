from __future__ import annotations

import base64
import hashlib
import os
import secrets
from typing import Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from fastapi import HTTPException


# Vault Encryption Keys
# In production, store this key in a secure vault (e.g., Windows DPAPI, HashiCorp Vault, or HSM).
# Never commit this key to version control.
VAULT_KEY_B64 = os.getenv("CHRONOFACT_VAULT_KEY_B64")

if VAULT_KEY_B64:
    VAULT_KEY = base64.urlsafe_b64decode(VAULT_KEY_B64.encode("ascii"))
    if len(VAULT_KEY) != 32:
        raise RuntimeError("Vault key must decode to exactly 32 bytes.")
else:
    VAULT_KEY = None


def protect_file(evidence_id: str, plaintext: bytes) -> bytes:
    """Encrypt evidence bytes using AES-GCM."""
    if VAULT_KEY is None:
        raise RuntimeError("Vault key not configured. Set CHRONOFACT_VAULT_KEY_B64.")
    nonce = os.urandom(12)
    ciphertext = AESGCM(VAULT_KEY).encrypt(nonce, plaintext, evidence_id.encode("ascii"))
    return b"CFV1" + nonce + ciphertext


def open_protected_file(evidence_id: str, protected: bytes) -> bytes:
    """Decrypt evidence bytes using AES-GCM."""
    if VAULT_KEY is None:
        raise RuntimeError("Vault key not configured.")
    if len(protected) < 4 + 12 + 16 or protected[:4] != b"CFV1":
        raise ValueError("Invalid or incomplete encrypted file.")
    nonce = protected[4:16]
    ciphertext = protected[16:]
    return AESGCM(VAULT_KEY).decrypt(nonce, ciphertext, evidence_id.encode("ascii"))


def generate_vault_key() -> str:
    """Generate a new vault key for setup."""
    key = secrets.token_bytes(32)
    return base64.urlsafe_b64encode(key).decode("ascii")
