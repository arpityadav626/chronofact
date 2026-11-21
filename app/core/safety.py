"""Small, dependency-free input-safety helpers (unit-tested in tests/test_safety_and_auth.py)."""
import re
import unicodedata
from pathlib import Path
from typing import Optional

_SAFE_CHARS = re.compile(r"[^A-Za-z0-9._\- ()\[\]]+")
_WINDOWS_RESERVED = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}


def sanitize_filename(name: Optional[str], default: str = "unnamed_exhibit.bin", max_len: int = 120) -> str:
    """
    Reduce a client-supplied filename to a safe basename:
    drops any directory part (both / and \\ separators), control chars, leading dots,
    reserved Windows device names and over-long names. Extension is preserved.
    """
    if not name:
        return default
    name = unicodedata.normalize("NFKC", str(name))
    name = name.replace("\\", "/").split("/")[-1]            # basename only (kills ../ and C:\\)
    name = _SAFE_CHARS.sub("_", name).strip(" .")
    if not name:
        return default
    stem, dot, ext = name.rpartition(".")
    if not dot:
        stem, ext = name, ""
    if stem.upper() in _WINDOWS_RESERVED:
        stem = "_" + stem
    if len(stem) + len(ext) + 1 > max_len:
        stem = stem[: max(1, max_len - len(ext) - 1)]
    return f"{stem}.{ext}" if ext else stem


def resolve_inside(base: Path, filename: str) -> Path:
    """Join base/filename and guarantee the result stays inside base (no traversal, no symlink escape)."""
    base_r = base.resolve()
    target = (base_r / filename).resolve()
    if target.parent != base_r:
        raise ValueError("Path escapes the evidence vault.")
    return target


def build_fts_query(text: str, min_len: int = 3, max_terms: int = 12) -> Optional[str]:
    """
    Turn free text into a SAFE SQLite FTS5 MATCH expression:
    every term is double-quoted (so FTS operators like AND/OR/NEAR/* and ':' column filters
    are treated as plain text) and terms are OR-ed together.
    """
    # keep IPs / e-mails / hostnames together as one quoted phrase (e.g. 192.168.1.105)
    words = re.findall(r"\w[\w.@:\-]*\w|\w", text or "", flags=re.UNICODE)
    words = [w for w in words if len(w) >= min_len][:max_terms]
    if not words:
        return None
    return " OR ".join('"' + w.replace('"', '""') + '"' for w in words)
