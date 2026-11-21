import sqlite3
import json
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Any, List, Optional
from .config import DB_PATH


@contextmanager
def get_db():
    """
    SQLite connection scope: commit on success, rollback on error, ALWAYS close.
    (A bare `with sqlite3.connect()` never closes the connection, which leaks handles.)
    """
    conn = sqlite3.connect(DB_PATH, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    try:
        yield conn
        conn.commit()
    except BaseException:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 1. Evidence items (The immutable evidence registry)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evidence_items (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                file_type TEXT NOT NULL,
                sha256 TEXT NOT NULL UNIQUE,
                size_bytes INTEGER NOT NULL,
                storage_path TEXT NOT NULL,
                source_description TEXT,
                uploaded_by TEXT DEFAULT 'Investigator',
                uploaded_at TEXT NOT NULL
            )
        """)
        try:
            cursor.execute("ALTER TABLE evidence_items ADD COLUMN sha3_256 TEXT")
        except sqlite3.OperationalError:
            pass
        
        # 2. Hash-chained audit log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                seq INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                actor TEXT NOT NULL,
                action TEXT NOT NULL,
                target_id TEXT NOT NULL,
                target_hash TEXT NOT NULL,
                details TEXT,
                prev_hash TEXT NOT NULL,
                entry_hash TEXT NOT NULL
            )
        """)
        
        # 3. Extracted atomic facts (with intervals [t_min, t_max] for hyper-timelines)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS extracted_facts (
                id TEXT PRIMARY KEY,
                evidence_id TEXT NOT NULL,
                fact_type TEXT NOT NULL,
                locator TEXT NOT NULL,
                raw_text TEXT NOT NULL,
                actor TEXT,
                t_min TEXT NOT NULL,
                t_max TEXT NOT NULL,
                tz_basis TEXT NOT NULL,
                time_reliability TEXT NOT NULL,
                FOREIGN KEY (evidence_id) REFERENCES evidence_items (id)
            )
        """)
        
        # 4. Entities (normalized emails, phone numbers, IPs, usernames)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                id TEXT PRIMARY KEY,
                entity_type TEXT NOT NULL,
                raw_value TEXT NOT NULL,
                normalized_value TEXT NOT NULL,
                first_seen_fact_id TEXT,
                UNIQUE(entity_type, normalized_value)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entity_mentions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_id TEXT NOT NULL,
                fact_id TEXT NOT NULL,
                FOREIGN KEY (entity_id) REFERENCES entities(id),
                FOREIGN KEY (fact_id) REFERENCES extracted_facts(id)
            )
        """)
        
        # 5. Detected inconsistencies (with mandatory benign explanations)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inconsistencies (
                id TEXT PRIMARY KEY,
                rule_id TEXT NOT NULL,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                fact_ids TEXT NOT NULL,
                benign_explanations TEXT NOT NULL,
                detected_at TEXT NOT NULL
            )
        """)
        
        # 6. FTS5 full-text search table for instant zero-dependency retrieval
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS facts_fts USING fts5(
                fact_id UNINDEXED,
                evidence_id UNINDEXED,
                raw_text,
                locator
            )
        """)
        
        # Initialize genesis block in audit log if empty (computed in Python: the old SQL
        # literal '0'*64 is a numeric multiplication in SQLite and stored the value 0).
        cursor.execute("SELECT COUNT(*) as cnt FROM audit_log")
        if cursor.fetchone()["cnt"] == 0:
            from .crypto import HashChainedAuditLogger
            g = HashChainedAuditLogger.create_log_entry(
                seq=1, actor="SYSTEM", action="GENESIS_INIT", target_id="SYSTEM",
                target_hash="0" * 64, prev_hash="0" * 64, details={"msg": "Audit Log Initialized"},
            )
            cursor.execute(
                """INSERT INTO audit_log (seq, timestamp, actor, action, target_id, target_hash, details, prev_hash, entry_hash)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (g["seq"], g["timestamp"], g["actor"], g["action"], g["target_id"], g["target_hash"],
                 g["details"], g["prev_hash"], g["entry_hash"]),
            )

        # Append-only enforcement at DB level (someone with raw file access can still drop these,
        # which is exactly what /api/audit/verify detects through the hash chain).
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS audit_log_no_update BEFORE UPDATE ON audit_log
            BEGIN SELECT RAISE(ABORT, 'audit_log is append-only'); END
        """)
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS audit_log_no_delete BEFORE DELETE ON audit_log
            BEGIN SELECT RAISE(ABORT, 'audit_log is append-only'); END
        """)
        conn.commit()
