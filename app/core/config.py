"""CHRONOFACT runtime configuration (environment driven)."""
import os
from pathlib import Path

try:  # optional: .env support
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:  # pragma: no cover
    pass

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = Path(os.getenv("CHRONOFACT_DATA_DIR", str(BASE_DIR / "data"))).resolve()
VAULT_DIR = DATA_DIR / "vault"
EXPORTS_DIR = DATA_DIR / "exports"
DB_PATH = DATA_DIR / "chronofact.db"

for _d in (DATA_DIR, VAULT_DIR, EXPORTS_DIR):
    _d.mkdir(parents=True, exist_ok=True)

APP_NAME = "CHRONOFACT"
APP_VERSION = "2.0.0"
LEGAL_FRAMEWORK = "Bharatiya Sakshya Adhiniyam, 2023 (BSA) Section 63(4)"

ENV = os.getenv("CHRONOFACT_ENV", "development").strip().lower()
IS_PRODUCTION = ENV == "production"
# Demo mode ONLY: seeds well-known demo accounts. Refused in production (see auth.py).
DEMO_MODE = os.getenv("CHRONOFACT_DEMO_MODE", "false").strip().lower() in ("1", "true", "yes")

MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_MB", "50")) * 1024 * 1024
ALLOW_RESET = os.getenv("CHRONOFACT_ALLOW_RESET", "false" if IS_PRODUCTION else "true").strip().lower() in ("1", "true", "yes")
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]
