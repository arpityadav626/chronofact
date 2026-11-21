"""Isolated test environment: temp data dir, throw-away accounts (never touches ./data)."""
import os, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("CHRONOFACT_DATA_DIR", tempfile.mkdtemp(prefix="chronofact_test_"))
os.environ.setdefault("CHRONOFACT_USER", "lead")
os.environ.setdefault("CHRONOFACT_PASSWORD", "CorrectHorse-Battery9")
os.environ.setdefault("CHRONOFACT_ANALYST_USER", "ana")
os.environ.setdefault("CHRONOFACT_ANALYST_PASSWORD", "Analyst-Passw0rd!!")
os.environ.setdefault("JWT_SECRET_KEY", "t" * 48)
