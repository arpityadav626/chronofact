import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
VAULT_DIR = DATA_DIR / "vault"
EXPORTS_DIR = DATA_DIR / "exports"
DB_PATH = DATA_DIR / "chronofact.db"

# Ensure runtime directories exist
for directory in [DATA_DIR, VAULT_DIR, EXPORTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Application metadata
APP_NAME = "CHRONOFACT"
APP_VERSION = "1.0.0"
LEGAL_FRAMEWORK = "Bharatiya Sakshya Adhiniyam, 2023 (BSA) Section 63(4)"
