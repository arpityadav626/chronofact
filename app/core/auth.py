"""
CHRONOFACT authentication (no third-party crypto dependency beyond PyJWT).

Design rules
------------
* NO hard-coded passwords and NO hard-coded signing secret.
  - Accounts come from environment variables (CHRONOFACT_USER / CHRONOFACT_PASSWORD, and optionally
    CHRONOFACT_ANALYST_USER / CHRONOFACT_ANALYST_PASSWORD).
  - If a password is not provided: production -> refuse to start; development -> a random one-time
    password is generated and printed once to the server console.
  - CHRONOFACT_DEMO_MODE=true seeds the publicly documented demo accounts (never allowed in production).
* Passwords are stored as scrypt hashes (hashlib.scrypt, per-user random salt, constant-time compare).
* JWT secret must be >= 32 chars in production; in development a random per-process secret is used.
* Failed logins are throttled per (client, username).
"""
import base64
import hashlib
import hmac
import logging
import os
import secrets
import sys
import threading
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt  # PyJWT

from .config import DEMO_MODE, IS_PRODUCTION

logger = logging.getLogger("chronofact.auth")

JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
_PLACEHOLDERS = {"", "change_this_in_production", "changeme", "secret"}

# Publicly documented demo credentials. Only ever active when CHRONOFACT_DEMO_MODE=true (not production).
DEMO_ACCOUNTS = {
    "examiner": ("SecurePassMin16Chars!", True),
    "analyst": ("ChronoFact2026!", False),
}


def _load_jwt_secret() -> str:
    secret = os.getenv("JWT_SECRET_KEY", "").strip()
    if secret.lower() in _PLACEHOLDERS or len(secret) < 32:
        if IS_PRODUCTION:
            raise RuntimeError(
                "JWT_SECRET_KEY missing/weak. Generate one: python -c \"import secrets; print(secrets.token_urlsafe(48))\""
            )
        logger.warning("JWT_SECRET_KEY not set (or < 32 chars): using a random per-process secret. "
                       "Tokens will be invalidated on every restart.")
        return secrets.token_urlsafe(48)
    return secret


JWT_SECRET_KEY = _load_jwt_secret()


# ------------------------------------------------------------------ password hashing (scrypt)
_SCRYPT_N, _SCRYPT_R, _SCRYPT_P = 2 ** 14, 8, 1


def get_password_hash(password: str) -> str:
    salt = os.urandom(16)
    dk = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=_SCRYPT_N, r=_SCRYPT_R, p=_SCRYPT_P, dklen=32)
    return "scrypt${}${}${}${}${}".format(
        _SCRYPT_N, _SCRYPT_R, _SCRYPT_P,
        base64.b64encode(salt).decode(), base64.b64encode(dk).decode(),
    )


def verify_password(plain_password: str, stored: str) -> bool:
    try:
        scheme, n, r, p, salt_b64, dk_b64 = stored.split("$")
        if scheme != "scrypt":
            return False
        salt, expected = base64.b64decode(salt_b64), base64.b64decode(dk_b64)
        dk = hashlib.scrypt(plain_password.encode("utf-8"), salt=salt, n=int(n), r=int(r), p=int(p), dklen=len(expected))
        return hmac.compare_digest(dk, expected)
    except Exception:
        return False


_DUMMY_HASH = get_password_hash(secrets.token_urlsafe(16))  # equalises timing for unknown usernames


# ------------------------------------------------------------------ user registry
def _build_registry() -> Dict[str, Dict[str, Any]]:
    users: Dict[str, Dict[str, Any]] = {}

    def add(username: str, password: str, superuser: bool, role: str):
        users[username] = {
            "username": username,
            "email": f"{username}@forensic-lab.local",
            "is_active": True,
            "is_superuser": superuser,
            "role": role,
            "hashed_password": get_password_hash(password),
        }

    if DEMO_MODE:
        if IS_PRODUCTION:
            raise RuntimeError("CHRONOFACT_DEMO_MODE must not be enabled when CHRONOFACT_ENV=production.")
        logger.warning("DEMO MODE ACTIVE: publicly documented demo accounts are enabled. Never expose this to a network.")
        for name, (pw, su) in DEMO_ACCOUNTS.items():
            add(name, pw, su, "examiner" if su else "analyst")

    user = os.getenv("CHRONOFACT_USER", "").strip()
    pw = os.getenv("CHRONOFACT_PASSWORD", "")
    if user:
        if not pw:
            if IS_PRODUCTION:
                raise RuntimeError("CHRONOFACT_PASSWORD is required in production.")
            pw = secrets.token_urlsafe(14)
            print(f"[CHRONOFACT] One-time generated password for '{user}': {pw}", file=sys.stderr)
        if len(pw) < 12:
            raise RuntimeError("CHRONOFACT_PASSWORD must be at least 12 characters.")
        add(user, pw, True, "examiner")

    a_user = os.getenv("CHRONOFACT_ANALYST_USER", "").strip()
    a_pw = os.getenv("CHRONOFACT_ANALYST_PASSWORD", "")
    if a_user and a_pw:
        if len(a_pw) < 12:
            raise RuntimeError("CHRONOFACT_ANALYST_PASSWORD must be at least 12 characters.")
        add(a_user, a_pw, False, "analyst")

    if not users:
        if IS_PRODUCTION:
            raise RuntimeError("No accounts configured. Set CHRONOFACT_USER and CHRONOFACT_PASSWORD.")
        name, pw = "examiner", secrets.token_urlsafe(14)
        add(name, pw, True, "examiner")
        print(f"[CHRONOFACT] No accounts configured. One-time login -> user: {name}  password: {pw}", file=sys.stderr)
    return users


examiners_db: Dict[str, Dict[str, Any]] = _build_registry()


def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    user = examiners_db.get((username or "").strip().lower()) or examiners_db.get((username or "").strip())
    if not user:
        verify_password(password or "", _DUMMY_HASH)  # constant-ish time
        return None
    if not user["is_active"] or not verify_password(password or "", user["hashed_password"]):
        return None
    return user


# ------------------------------------------------------------------ tokens
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    now = datetime.now(timezone.utc)
    payload = {**data, "iat": now, "exp": now + (expires_delta or timedelta(minutes=JWT_EXPIRE_MINUTES))}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM], options={"require": ["exp", "sub"]})
    except jwt.PyJWTError:
        return None


def user_from_token(token: str) -> Optional[Dict[str, Any]]:
    """Resolve a bearer token to a CURRENT, active account (deleted/disabled users lose access immediately)."""
    payload = decode_token(token)
    if not payload:
        return None
    user = examiners_db.get(payload.get("sub"))
    if not user or not user["is_active"]:
        return None
    return {"username": user["username"], "role": user["role"], "is_superuser": user["is_superuser"]}


# ------------------------------------------------------------------ throttling
class RateLimiter:
    """Sliding-window limiter (in-memory, single process)."""

    def __init__(self, max_requests: int = 100, period_seconds: int = 60):
        self.max_requests = max_requests
        self.period_seconds = period_seconds
        self._hits: Dict[str, list] = defaultdict(list)
        self._lock = threading.Lock()

    def is_allowed(self, client_id: str) -> bool:
        now = time.time()
        with self._lock:
            hits = [t for t in self._hits[client_id] if now - t < self.period_seconds]
            if len(hits) >= self.max_requests:
                self._hits[client_id] = hits
                return False
            hits.append(now)
            self._hits[client_id] = hits
            if len(self._hits) > 10000:  # bound memory
                for k in [k for k, v in self._hits.items() if not v or now - v[-1] >= self.period_seconds]:
                    self._hits.pop(k, None)
            return True


class LoginThrottle:
    """Lock a (client, username) pair for `lock_seconds` after `max_failures` consecutive failures."""

    def __init__(self, max_failures: int = 5, lock_seconds: int = 300):
        self.max_failures, self.lock_seconds = max_failures, lock_seconds
        self._state: Dict[str, Dict[str, float]] = {}
        self._lock = threading.Lock()

    @staticmethod
    def _key(client: str, username: str) -> str:
        return f"{client}|{(username or '').strip().lower()}"

    def seconds_locked(self, client: str, username: str) -> int:
        with self._lock:
            st = self._state.get(self._key(client, username))
            if not st:
                return 0
            remaining = int(st["locked_until"] - time.time())
            return max(0, remaining)

    def record_failure(self, client: str, username: str) -> None:
        with self._lock:
            st = self._state.setdefault(self._key(client, username), {"fails": 0, "locked_until": 0.0})
            st["fails"] += 1
            if st["fails"] >= self.max_failures:
                st["locked_until"] = time.time() + self.lock_seconds
                st["fails"] = 0

    def record_success(self, client: str, username: str) -> None:
        with self._lock:
            self._state.pop(self._key(client, username), None)


rate_limiter = RateLimiter(
    max_requests=int(os.getenv("RATE_LIMIT_REQUESTS", "100")),
    period_seconds=int(os.getenv("RATE_LIMIT_PERIOD", "60")),
)
login_throttle = LoginThrottle()
login_ip_limiter = RateLimiter(max_requests=20, period_seconds=60)  # raw attempts per IP per minute
