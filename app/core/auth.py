"""
CHRONOFACT Authentication & Security Module
=============================================
JWT-based authentication for forensic investigation workbench.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel
import os

from dotenv import load_dotenv

load_dotenv()

# Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "CHANGE_THIS_IN_PRODUCTION")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

import bcrypt

def get_password_hash(password: str) -> str:
    """Hash password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8")[:72], bcrypt.gensalt()).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash using bcrypt."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8")[:72], hashed_password.encode("utf-8"))
    except Exception:
        return False


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username: str
    email: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False


class UserInDB(User):
    hashed_password: str


# Mock user database (replace with real DB in production)
fake_users_db = {
    "forensic_examiner": {
        "username": "forensic_examiner",
        "email": "examiner@cybercrime.gov.in",
        "is_active": True,
        "is_superuser": True,
        "hashed_password": get_password_hash("SecurePassword123!")
    }
}


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Authenticate user against database."""
    if username not in fake_users_db:
        return None
    user = fake_users_db[username]
    if not verify_password(password, user["hashed_password"]):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


# Rate limiting (simple in-memory implementation)
from collections import defaultdict
import time


class RateLimiter:
    """Simple token bucket rate limiter."""
    
    def __init__(self, max_requests: int = 100, period_seconds: int = 60):
        self.max_requests = max_requests
        self.period_seconds = period_seconds
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed."""
        now = time.time()
        # Clean old requests
        self.requests[client_id] = [
            r for r in self.requests[client_id] 
            if now - r < self.period_seconds
        ]
        
        if len(self.requests[client_id]) < self.max_requests:
            self.requests[client_id].append(now)
            return True
        return False


rate_limiter = RateLimiter(
    max_requests=int(os.getenv("RATE_LIMIT_REQUESTS", "100")),
    period_seconds=int(os.getenv("RATE_LIMIT_PERIOD", "60"))
)
