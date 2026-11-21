"""
CHRONOFACT 2.0 - FastAPI backend.

Security model (v2):
  * Every /api/* route except /api/health and /api/auth/* requires a valid bearer token.
  * Evidence is written to the vault only after filename sanitisation + path confinement.
  * Audit entries are appended inside the same DB transaction as the action they describe.
  * Nothing in this module fabricates evidence: a missing exhibit is reported as an integrity problem.
"""
import hashlib
import json
import logging
import os
import sqlite3
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .core.config import (
    ALLOW_RESET, APP_NAME, APP_VERSION, BASE_DIR, CORS_ORIGINS, IS_PRODUCTION, MAX_UPLOAD_BYTES, VAULT_DIR,
)
from .core.auth import (
    authenticate_user, create_access_token, login_ip_limiter, login_throttle, user_from_token,
)
from .core.crypto import append_audit_entry, verify_audit_chain
from .core.database import get_db, init_db
from .core.forensic_hasher import (
    ForensicHashEngine, ForensicIntegrityViolationError, MerkleTreeEngine, verify_case_integrity,
)
from .core.safety import build_fts_query, resolve_inside, sanitize_filename
from .core.security import add_security_headers, rate_limit_middleware
from .engines.entity_extractor import extract_all_entities
from .engines.inconsistency import detect_inconsistencies
from .engines.ml_anomaly import ForensicLogAnomalyModel
from .engines.ml_engine import global_ml_engine
from .engines.rag_engine import RAGEngine
from .engines.timeline_engine import build_interval_timeline
from .engines.training_pipeline import TrainingPipeline
from .engines.verifier import MechanicalCitationVerifier
from .legal.bsa_certificate import generate_bsa_section_63_certificate
from .parsers.chat_parser import parse_chat_file
from .parsers.csv_log_parser import parse_csv_log_file
from .parsers.email_parser import parse_eml_file

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("chronofact")

LOG_FACT_TYPES = ("SERVER_LOG_EVENT", "SERVER_LOG", "AUTH_EVENT", "FILE_TRANSFER")
_LOG_FACT_SQL = "SELECT * FROM extracted_facts WHERE fact_type IN ({})".format(",".join("?" * len(LOG_FACT_TYPES)))


# --------------------------------------------------------------------------- app + middleware
@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    logger.info("%s %s started (env=%s)", APP_NAME, APP_VERSION, "production" if IS_PRODUCTION else "development")
    yield


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url=None if IS_PRODUCTION else "/api/docs",
    redoc_url=None if IS_PRODUCTION else "/api/redoc",
    openapi_url=None if IS_PRODUCTION else "/api/openapi.json",
)

# Same-origin by default. Cross-origin access must be opted into explicitly (CORS_ORIGINS=https://a,https://b).
# Bearer tokens travel in the Authorization header (no cookies) so credentials are not allowed cross-site.
if CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type"],
    )
app.middleware("http")(rate_limit_middleware)
app.middleware("http")(add_security_headers)


# --------------------------------------------------------------------------- auth
bearer = HTTPBearer(auto_error=False)


class Token(BaseModel):
    access_token: str
    token_type: str


def require_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer)) -> Dict[str, Any]:
    if not credentials:
        raise HTTPException(401, "Authentication required", headers={"WWW-Authenticate": "Bearer"})
    user = user_from_token(credentials.credentials)
    if not user:
        raise HTTPException(401, "Invalid or expired token", headers={"WWW-Authenticate": "Bearer"})
    return user


def require_admin(user: Dict[str, Any] = Depends(require_user)) -> Dict[str, Any]:
    if not user.get("is_superuser"):
        raise HTTPException(403, "Administrator (lead examiner) role required")
    return user


@app.post("/api/auth/login", response_model=Token)
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    client = request.client.host if request.client else "unknown"
    if not login_ip_limiter.is_allowed(client):
        raise HTTPException(429, "Too many login attempts. Slow down.")
    wait = login_throttle.seconds_locked(client, username)
    if wait:
        raise HTTPException(429, f"Too many failed attempts. Try again in {wait} s.", headers={"Retry-After": str(wait)})
    user = authenticate_user(username, password)
    if not user:
        login_throttle.record_failure(client, username)
        raise HTTPException(401, "Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    login_throttle.record_success(client, username)
    return Token(access_token=create_access_token({"sub": user["username"], "role": user["role"]}), token_type="bearer")


@app.post("/api/auth/verify")
def verify_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer)):
    user = user_from_token(credentials.credentials) if credentials else None
    return {"valid": bool(user), "user": {"username": user["username"], "role": user["role"]} if user else None}


@app.get("/api/health")
def health_check():
    return {"status": "ONLINE", "app": APP_NAME, "version": APP_VERSION}


# --------------------------------------------------------------------------- static UI
STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
ASSETS_DIR = STATIC_DIR / "assets"
if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")


@app.get("/", response_class=HTMLResponse)
@app.get("/login", response_class=HTMLResponse)
@app.get("/login.html", response_class=HTMLResponse)
def serve_login():
    path = STATIC_DIR / "login.html"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return HTMLResponse("<h1>Login page not found</h1>", status_code=404)


@app.get("/index.html", response_class=HTMLResponse)
@app.get("/workbench", response_class=HTMLResponse)
def serve_index():
    path = STATIC_DIR / "index.html"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return HTMLResponse("<h1>CHRONOFACT is running. Open /static/index.html</h1>")


@app.get("/styles.css")
def serve_styles():
    return FileResponse(STATIC_DIR / "styles.css", media_type="text/css")


@app.get("/app.js")
def serve_app_js():
    return FileResponse(STATIC_DIR / "app.js", media_type="application/javascript")


# --------------------------------------------------------------------------- protected API
protected = APIRouter(dependencies=[Depends(require_user)])


def _type_from_extension(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext in (".eml", ".msg"):
        return "EMAIL"
    if ext in (".txt", ".chat"):
        return "CHAT_EXPORT"
    if ext in (".csv", ".log"):
        return "SERVER_LOG"
    return "GENERIC_DOCUMENT"


def process_evidence_ingestion(
    filename: str,
    file_bytes: bytes,
    source_description: str = "Lawfully seized evidence exhibit",
    uploaded_by: str = "examiner",
) -> Dict[str, Any]:
    original_name = "".join(ch for ch in str(filename) if ch.isprintable())[:255]
    safe_name = sanitize_filename(filename)
    evidence_id = f"EV-{uuid.uuid4().hex[:8].upper()}"
    file_path = resolve_inside(VAULT_DIR, f"{evidence_id}_{safe_name}")
    now_utc = datetime.now(timezone.utc).isoformat()
    ftype = _type_from_extension(safe_name)

    with open(file_path, "xb") as f_out:  # 'x': never overwrite an existing exhibit
        f_out.write(file_bytes)

    try:
        digest = ForensicHashEngine.compute_dual_hash(file_path, evidence_id=evidence_id, preserve_timestamps=True)
        sha256_hash, sha3_256_hash, file_size = digest.sha256, digest.sha3_256, digest.size_bytes

        with get_db() as conn:
            conn.execute("BEGIN IMMEDIATE")  # serialise writers so the audit chain cannot fork
            cursor = conn.cursor()
            cursor.execute("SELECT id, filename FROM evidence_items WHERE sha256 = ?", (sha256_hash,))
            existing = cursor.fetchone()
            if existing:
                append_audit_entry(cursor, uploaded_by, "EVIDENCE_DUPLICATE_REJECTED", existing["id"], sha256_hash,
                                   {"attempted_filename": original_name})
                result = {
                    "status": "ALREADY_INGESTED",
                    "evidence_id": existing["id"],
                    "filename": existing["filename"],
                    "sha256": sha256_hash,
                    "sha3_256": sha3_256_hash,
                    "message": f"Exhibit already exists in vault with identical SHA-256 (ID: {existing['id']})",
                }
                duplicate = True
            else:
                duplicate = False
                cursor.execute(
                    """INSERT INTO evidence_items
                       (id, filename, file_type, sha256, sha3_256, size_bytes, storage_path, source_description, uploaded_by, uploaded_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (evidence_id, safe_name, ftype, sha256_hash, sha3_256_hash, file_size, str(file_path),
                     str(source_description)[:500], str(uploaded_by), now_utc),
                )
                append_audit_entry(cursor, uploaded_by, "EVIDENCE_INGESTION_DUAL_HASH", evidence_id, sha256_hash,
                                   {"filename": safe_name, "original_filename": original_name, "file_type": ftype,
                                    "size_bytes": file_size, "sha3_256": sha3_256_hash})

                if ftype == "EMAIL":
                    extracted_facts = parse_eml_file(file_path, evidence_id)["facts"]
                elif ftype == "CHAT_EXPORT":
                    extracted_facts = parse_chat_file(file_path, evidence_id)["facts"]
                elif ftype == "SERVER_LOG":
                    extracted_facts = parse_csv_log_file(file_path, evidence_id)["facts"]
                else:
                    raw_txt = file_path.read_text(encoding="utf-8", errors="replace")
                    extracted_facts = [{
                        "id": f"F-DOC-{uuid.uuid4().hex[:8]}",
                        "evidence_id": evidence_id,
                        "fact_type": "DOCUMENT_ARTIFACT",
                        "locator": "Full Document",
                        "raw_text": raw_txt[:2000],
                        "actor": str(uploaded_by),
                        "t_min": now_utc,
                        "t_max": now_utc,
                        "tz_basis": "ingest_timestamp",
                        "time_reliability": "ingest_clock",
                    }]

                for f in extracted_facts:
                    cursor.execute(
                        """INSERT INTO extracted_facts
                           (id, evidence_id, fact_type, locator, raw_text, actor, t_min, t_max, tz_basis, time_reliability)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (f["id"], f["evidence_id"], f["fact_type"], f["locator"], f["raw_text"], f.get("actor", ""),
                         f["t_min"], f["t_max"], f["tz_basis"], f["time_reliability"]),
                    )
                    cursor.execute(
                        "INSERT INTO facts_fts (fact_id, evidence_id, raw_text, locator) VALUES (?, ?, ?, ?)",
                        (f["id"], f["evidence_id"], f["raw_text"], f["locator"]),
                    )
                result = {
                    "status": "SUCCESS",
                    "evidence_id": evidence_id,
                    "filename": safe_name,
                    "sha256": sha256_hash,
                    "sha3_256": sha3_256_hash,
                    "facts_extracted": len(extracted_facts),
                }
    except BaseException:
        file_path.unlink(missing_ok=True)  # transaction rolled back -> do not leave an orphan exhibit
        raise

    if duplicate:
        file_path.unlink(missing_ok=True)  # the identical exhibit is already vaulted
    else:
        recheck_inconsistencies()
    return result


@protected.post("/api/upload")
async def upload_evidence(
    file: UploadFile = File(...),
    source_description: str = Form("Lawfully seized evidence exhibit"),
    user: Dict[str, Any] = Depends(require_user),
):
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, f"File exceeds the {MAX_UPLOAD_BYTES // (1024 * 1024)} MB limit")
    if not content:
        raise HTTPException(400, "Empty file")
    # actor is the authenticated account - never a client-supplied name
    return await run_in_threadpool(
        process_evidence_ingestion, file.filename or "unnamed_exhibit.bin", content, source_description, user["username"]
    )


def recheck_inconsistencies():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM extracted_facts")
        facts = [dict(r) for r in cursor.fetchall()]
        cursor.execute("SELECT * FROM evidence_items")
        evidence = [dict(r) for r in cursor.fetchall()]
        detected = detect_inconsistencies(facts, evidence)
        cursor.execute("DELETE FROM inconsistencies")
        for inc in detected:
            cursor.execute(
                """INSERT INTO inconsistencies (id, rule_id, category, title, description, fact_ids, benign_explanations, detected_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (inc["id"], inc["rule_id"], inc["category"], inc["title"], inc["description"],
                 json.dumps(inc["fact_ids"]), json.dumps(inc["benign_explanations"]), inc["detected_at"]),
            )


@protected.get("/api/evidence")
def list_evidence():
    with get_db() as conn:
        items = [dict(r) for r in conn.execute("SELECT * FROM evidence_items ORDER BY uploaded_at DESC").fetchall()]
    return {"evidence_items": items}


@protected.get("/api/evidence/{evidence_id}/inspect")
def inspect_evidence_file(evidence_id: str):
    with get_db() as conn:
        item = conn.execute("SELECT * FROM evidence_items WHERE id = ?", (evidence_id,)).fetchone()
    if not item:
        raise HTTPException(404, "Evidence exhibit not found")
    item = dict(item)

    file_path = Path(item["storage_path"])
    if not file_path.is_file():
        # Never substitute made-up bytes: a missing exhibit is itself a chain-of-custody failure.
        raise HTTPException(410, "Exhibit file is missing from the vault - treat as an integrity violation and escalate.")
    raw_bytes = file_path.read_bytes()

    magic_hex = " ".join(f"{b:02X}" for b in raw_bytes[:8])
    anomalies: List[Dict[str, Any]] = []
    ext = Path(item["filename"]).suffix.lower().lstrip(".")
    magic_status, magic_desc = "MATCH", "Valid Plain Text (ASCII/UTF-8)"

    actual_sha256 = hashlib.sha256(raw_bytes).hexdigest()
    if actual_sha256 != item["sha256"]:
        anomalies.append({
            "rule_id": "TAMPER-HASH-00", "title": "Vault file no longer matches ledger SHA-256", "severity": "CRITICAL",
            "start_byte": 0, "end_byte": max(0, len(raw_bytes) - 1),
            "explanation": f"Ledger SHA-256 {item['sha256']} != recomputed {actual_sha256}.",
        })

    if ext in ("csv", "txt", "log", "json", "eml"):
        if raw_bytes[:4] == b"PK\x03\x04":
            magic_status, magic_desc = "MISMATCH", "PK ZIP / Office OpenXML Container (50 4B 03 04)"
            anomalies.append({"rule_id": "TAMPER-MAGIC-03", "title": "Magic Byte Spoofing (ZIP Container)", "severity": "CRITICAL",
                              "start_byte": 0, "end_byte": 3,
                              "explanation": f"Exhibit extension is .{ext} but initial magic bytes match a PK ZIP container."})
        elif raw_bytes[:2] == b"MZ":
            magic_status, magic_desc = "MISMATCH", "Windows Portable Executable (4D 5A)"
            anomalies.append({"rule_id": "TAMPER-MAGIC-03", "title": "Executable Masquerading (PE Header)", "severity": "CRITICAL",
                              "start_byte": 0, "end_byte": 1, "explanation": "Exhibit header matches Windows Portable Executable (MZ)."})

    crlf = lf = cr = 0
    newline_records = []
    line_num, i, n = 1, 0, len(raw_bytes)
    while i < n:
        b = raw_bytes[i]
        if b == 0x0D:
            if i + 1 < n and raw_bytes[i + 1] == 0x0A:
                crlf += 1
                newline_records.append((i, "CRLF", line_num))
                i += 1
            else:
                cr += 1
                newline_records.append((i, "CR", line_num))
            line_num += 1
        elif b == 0x0A:
            lf += 1
            newline_records.append((i, "LF", line_num))
            line_num += 1
        i += 1

    dominant = "LF" if lf >= crlf else "CRLF"
    if lf > 0 and crlf > 0:
        for offset, nl_type, l_num in newline_records:
            if nl_type != dominant:
                anomalies.append({
                    "rule_id": "TAMPER-NEWLINE-01",
                    "title": f"Mixed Line Ending ({nl_type} vs Dominant {dominant})", "severity": "MEDIUM",
                    "start_byte": offset, "end_byte": offset + (2 if nl_type == "CRLF" else 1) - 1, "line_number": l_num,
                    "explanation": f"Non-standard newline sequence detected at Byte 0x{offset:04X} (Line {l_num}).",
                })

    pos = raw_bytes.find(b"\xE2\x80\x8B")
    while pos != -1:
        anomalies.append({"rule_id": "TAMPER-UNICODE-02", "title": "Hidden Zero-Width Space (U+200B)", "severity": "HIGH",
                          "start_byte": pos, "end_byte": pos + 2,
                          "explanation": f"Invisible Unicode Zero-Width Space (U+200B, bytes E2 80 8B) detected at Byte 0x{pos:04X}."})
        pos = raw_bytes.find(b"\xE2\x80\x8B", pos + 3)

    deduction = sum(35 if a["severity"] == "CRITICAL" else 25 if a["severity"] == "HIGH" else 15 for a in anomalies)
    total_anomalies = len(anomalies)
    return {
        "evidence_id": item["id"],
        "filename": item["filename"],
        "sha256": item["sha256"],
        "sha256_recomputed": actual_sha256,
        "hash_matches_ledger": actual_sha256 == item["sha256"],
        "size_bytes": len(raw_bytes),
        "file_type": item["file_type"],
        "magic_bytes_hex": magic_hex,
        "magic_status": magic_status,
        "magic_description": magic_desc,
        "dominant_newline": dominant,
        "newline_breakdown": {"lf": lf, "crlf": crlf, "cr": cr},
        "anomalies": anomalies[:200],
        "total_anomalies": total_anomalies,
        "integrity_score": max(0, 100 - deduction),
    }


@protected.get("/api/integrity/verify")
def api_verify_case_integrity():
    """Re-reads every vault file, recomputes both digests and the Merkle root."""
    try:
        return verify_case_integrity()
    except ForensicIntegrityViolationError as exc:
        return JSONResponse(status_code=409, content={"status": "FORENSIC_INTEGRITY_VIOLATION", "error": exc.to_dict()})


@protected.get("/api/audit/verify")
def api_verify_audit_chain():
    """Recomputes the whole hash chain of the audit log."""
    with get_db() as conn:
        rows = [dict(r) for r in conn.execute("SELECT * FROM audit_log ORDER BY seq ASC").fetchall()]
    return verify_audit_chain(rows)


@protected.get("/api/merkle")
def api_get_case_merkle_tree():
    with get_db() as conn:
        exhibits = [dict(r) for r in conn.execute(
            "SELECT id, filename, file_type, sha256, size_bytes FROM evidence_items ORDER BY uploaded_at ASC").fetchall()]
    return MerkleTreeEngine.build_merkle_tree(exhibits)


@protected.get("/api/timeline")
def get_timeline():
    with get_db() as conn:
        facts = [dict(r) for r in conn.execute("SELECT * FROM extracted_facts").fetchall()]
    return {"timeline_events": build_interval_timeline(facts)}


@protected.get("/api/inconsistencies")
def get_inconsistencies():
    recheck_inconsistencies()
    with get_db() as conn:
        raw_items = [dict(r) for r in conn.execute("SELECT * FROM inconsistencies ORDER BY detected_at DESC").fetchall()]
    for item in raw_items:
        item["fact_ids"] = json.loads(item["fact_ids"])
        item["benign_explanations"] = json.loads(item["benign_explanations"])
    return {"inconsistencies": raw_items}


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)


def _vault_text_map(with_filename: bool = False) -> Dict[str, str]:
    with get_db() as conn:
        items = [dict(r) for r in conn.execute("SELECT id, storage_path FROM evidence_items").fetchall()]
    vault_map: Dict[str, str] = {}
    for ev in items:
        p = Path(ev["storage_path"])
        vault_map[ev["id"]] = p.read_text(encoding="utf-8", errors="replace") if p.is_file() else ""
    return vault_map


@protected.post("/api/query")
def query_case_evidence(req: QueryRequest):
    retrieved_facts: List[Dict[str, Any]] = []
    fts_expr = build_fts_query(req.query)
    with get_db() as conn:
        if fts_expr:
            try:
                rows = conn.execute(
                    """SELECT f.* FROM facts_fts s JOIN extracted_facts f ON s.fact_id = f.id
                       WHERE facts_fts MATCH ? LIMIT 10""", (fts_expr,)).fetchall()
                retrieved_facts = [dict(r) for r in rows]
            except sqlite3.Error as exc:
                logger.warning("FTS query failed (%s) for expression %r", exc, fts_expr)
        if not retrieved_facts:
            retrieved_facts = [dict(r) for r in conn.execute(
                "SELECT * FROM extracted_facts ORDER BY t_min DESC LIMIT 6").fetchall()]
    return MechanicalCitationVerifier.answer_and_verify_query(
        query=req.query,
        evidence_vault_map=_vault_text_map(),
        stored_facts_map={f["id"]: f for f in retrieved_facts},
    )


# One shared engine: the previous code built a fresh, empty RAGEngine on every request, so
# /api/rag/index indexed a throw-away object and /api/rag/query always searched nothing.
_rag_engine = RAGEngine()


def _rebuild_rag_index() -> Dict[str, int]:
    with get_db() as conn:
        items = [dict(r) for r in conn.execute("SELECT id, storage_path, filename FROM evidence_items").fetchall()]
    documents, counter = [], 0
    for ev in items:
        p = Path(ev["storage_path"])
        if not p.is_file():
            continue
        for line_no, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            if line.strip():
                documents.append({"id": f"CHUNK-{counter}", "text": line,
                                  "metadata": {"evidence_id": ev["id"], "filename": ev.get("filename"), "line": line_no}})
                counter += 1
    _rag_engine.indexed_docs = []
    _rag_engine.index_documents(documents)
    return {"chunks_indexed": len(documents), "exhibits": len(items)}


@protected.post("/api/rag/index")
def rag_index():
    stats = _rebuild_rag_index()
    return {"status": "SUCCESS", **stats, "method": "sentence-transformers" if _rag_engine.model is not None else "keyword-fallback"}


@protected.post("/api/rag/query")
def rag_query(req: QueryRequest):
    if not _rag_engine.indexed_docs:
        _rebuild_rag_index()
    vault_map = _vault_text_map()
    results = []
    for hit in _rag_engine.search(req.query, top_k=5):
        meta = hit.get("metadata", {})
        text = hit.get("text", "")
        results.append({
            "id": hit.get("id"),
            "text": text,
            "evidence_id": meta.get("evidence_id"),
            "line": meta.get("line"),
            "similarity": round(float(hit.get("similarity", 0)), 4),
            "verbatim_in_exhibit": bool(text) and text in vault_map.get(meta.get("evidence_id"), ""),
        })
    entities: Dict[str, List[str]] = {}
    for r in results:
        for k, v in extract_all_entities(r["text"]).items():
            entities.setdefault(k, []).extend(v)
    return {
        "query": req.query,
        "status": "SUCCESS",
        "method": "sentence-transformers" if _rag_engine.model is not None else "keyword-fallback",
        "rag_results": results,
        "entities": {k: sorted(set(v)) for k, v in entities.items()},
    }


@protected.get("/api/ml/anomalies")
def get_ml_log_anomalies(contamination: float = 0.2):
    if not 0.01 <= contamination <= 0.5:
        raise HTTPException(422, "contamination must be between 0.01 and 0.5")
    with get_db() as conn:
        log_facts = [dict(r) for r in conn.execute(_LOG_FACT_SQL, LOG_FACT_TYPES).fetchall()]
        if not log_facts:
            log_facts = [dict(r) for r in conn.execute("SELECT * FROM extracted_facts").fetchall()]
    anomalies = ForensicLogAnomalyModel(contamination=contamination).fit_and_predict(log_facts)
    return {
        "status": "SUCCESS",
        "total_analyzed": len(log_facts),
        "anomalies_detected": sum(1 for a in anomalies if a["is_anomaly"]),
        "contamination": contamination,
        "note": "IsolationForest flags roughly the `contamination` fraction of ANY dataset by construction. "
                "Treat results as ranked review leads, not findings.",
        "anomalies": anomalies,
    }


@protected.get("/api/ml/status")
def get_ml_status():
    vault_map = _vault_text_map()
    global_ml_engine.index_vault(vault_map)
    vocab = len(global_ml_engine.vectorizer.vocabulary_) if global_ml_engine.vectorizer else 0
    return {
        "status": "READY",
        "algorithm": "Hybrid TF-IDF Vector Space + IsolationForest",
        "indexed_chunks": len(global_ml_engine.indexed_chunks),
        "vocabulary_features": vocab,
        "exhibits_in_vault": len(vault_map),
        "citation_gate": "ACTIVE (verbatim byte-span verification)",
        "supported_models": ["TF-IDF retrieval", "IsolationForest outlier detector", "Persistable anomaly model (ml_model.py)"],
    }


def get_log_facts_from_db() -> List[Dict[str, Any]]:
    with get_db() as conn:
        return [dict(r) for r in conn.execute(_LOG_FACT_SQL, LOG_FACT_TYPES).fetchall()]


@protected.post("/api/ml/train")
def train_anomaly_model(contamination: float = 0.15, use_synthetic_labels: bool = True):
    """Train a persistable anomaly model on ingested log facts (synthetic labels => smoke-test metrics only)."""
    if not 0.01 <= contamination <= 0.5:
        raise HTTPException(422, "contamination must be between 0.01 and 0.5")
    log_facts = get_log_facts_from_db()
    if not log_facts:
        return {"status": "INSUFFICIENT_DATA", "message": "No server log facts available for training. Upload server logs first."}
    pipeline = TrainingPipeline()
    report = (pipeline.train_with_synthetic_labels(log_facts, contamination=contamination)
              if use_synthetic_labels else pipeline.train(log_facts, contamination=contamination))
    return {
        "status": "TRAINING_COMPLETE",
        "model_id": report["model_id"],
        "n_training_samples": report["n_training_samples"],
        "evaluation_metrics": report.get("evaluation_metrics", {}),
        "evaluation_note": "Metrics computed against synthetic labels are NOT real-world accuracy." if use_synthetic_labels else "",
        "artifacts": report["artifacts"],
    }


@protected.get("/api/ml/models")
def list_trained_models():
    return {"models": TrainingPipeline().list_models(), "status": "SUCCESS"}


@protected.post("/api/ml/retrain-on-demand")
def retrain_on_demand():
    if len(get_log_facts_from_db()) < 4:
        return {"status": "INSUFFICIENT_DATA", "min_facts_needed": 4}
    return train_anomaly_model()


def _load_model_by_id(model_id: str):
    from .engines.ml_model import ForensicAnomalyModel
    pipeline = TrainingPipeline()
    target = next((m for m in pipeline.list_models() if m["model_id"] == model_id), None)
    if not target:
        return None, None
    return ForensicAnomalyModel(model_path=str(Path(pipeline.models_dir) / target["manifest_path"])), target


@protected.get("/api/ml/model/{model_id}/predict")
def predict_with_model(model_id: str, evidence_id: Optional[str] = None):
    model, _ = _load_model_by_id(model_id)
    if model is None:
        return {"status": "MODEL_NOT_FOUND", "model_id": model_id}
    anomalies = model.predict(get_log_facts_from_db())
    return {"status": "SUCCESS", "model_id": model_id,
            "anomalies_detected": sum(1 for a in anomalies if a["is_anomaly"]), "anomalies": anomalies[:20]}


@protected.get("/api/ml/model/{model_id}")
def get_model_status(model_id: str):
    try:
        model, target = _load_model_by_id(model_id)
        if model is None:
            return {"status": "MODEL_NOT_FOUND", "model_id": model_id}
        return {"status": "READY", "model_status": model.get_status(), "artifacts": target}
    except Exception as exc:
        logger.exception("model load failed")
        return {"status": "MODEL_LOAD_ERROR", "model_id": model_id, "error": str(exc)}


@protected.get("/api/certificate/bsa63")
def get_bsa_certificate(
    case_no: str = "[CASE NUMBER - TO BE FILLED]",
    investigator: str = "[NAME OF CERTIFYING OFFICER]",
    designation: str = "[DESIGNATION]",
    agency: str = "[AGENCY / LABORATORY]",
    user: Dict[str, Any] = Depends(require_user),
):
    """Generates an UNSIGNED DRAFT. Part A and Part B must be signed by the named human persons."""
    with get_db() as conn:
        evidence = [dict(r) for r in conn.execute("SELECT * FROM evidence_items").fetchall()]
        audit_chain = [dict(r) for r in conn.execute("SELECT * FROM audit_log ORDER BY seq ASC").fetchall()]
    cert = generate_bsa_section_63_certificate(
        case_number=case_no, investigator_name=investigator, investigator_designation=designation,
        organization=agency, evidence_items=evidence, audit_chain=audit_chain,
    )
    cert["status"] = "DRAFT_UNSIGNED - not valid until signed by the certifying officer (Part A) and expert (Part B)"
    cert["generated_by_account"] = user["username"]
    cert["audit_chain_check"] = verify_audit_chain(audit_chain)["status"]
    return cert


SAMPLE_FILES = {
    "confidential_leak.eml": (
        "From: vikram.malhotra@techcorp.in\n"
        "To: external.contact@protonmail.com\n"
        "Subject: Leaked Q3 Financial Model and Database Credentials\n"
        "Date: Fri, 12 Sep 2025 15:30:00 +0530\n"
        "Message-ID: <leak-8921-techcorp@corp>\n\n"
        "Attached is the unreleased patent draft and SQL credentials for production.\n"
        "Please confirm receipt and deposit the agreed consultation fee.\n"
    ),
    "whatsapp_chat.txt": (
        "[12/09/2025, 15:20:10] Team Lead: Vikram are you available on Slack for urgent sync?\n"
        "[12/09/2025, 15:25:40] Vikram Malhotra: Sir I am suffering from high fever, I am asleep in bed and completely offline till tomorrow morning.\n"
        "[12/09/2025, 15:26:00] Team Lead: Ok take rest.\n"
    ),
    "server_access.csv": (
        "timestamp,user,ip_address,action,status\n"
        "2025-09-12T15:24:10+05:30,vikram.malhotra,192.168.1.105,LOGIN,OK\n"
        "2025-09-12T15:28:45+05:30,vikram.malhotra,192.168.1.105,DOWNLOAD_FILE,CONFIDENTIAL_Q3_FINANCIALS.XLSX\n"
        "2025-09-12T15:31:00+05:30,vikram.malhotra,192.168.1.105,EXPORT_PATENT_DRAFT,OK\n"
    ),
    "telecom_cdr_tower.csv": (
        "timestamp,msisdn,cell_tower_id,azimuth,latitude,longitude,duration_sec\n"
        "2025-09-12T15:27:12+05:30,+91-9876543210,DEL-S-041,120,28.5355,77.2732,45\n"
    ),
}


@protected.post("/api/load-sample")
def load_sample_case(user: Dict[str, Any] = Depends(require_user)):
    sample_dir = BASE_DIR / "sample_evidence" / "case_01"
    sample_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for name, content in SAMPLE_FILES.items():
        path = sample_dir / name
        if not path.exists():  # never overwrite the repository's own sample files
            path.write_text(content, encoding="utf-8")
        results.append(process_evidence_ingestion(
            filename=name, file_bytes=path.read_bytes(),
            source_description=f"Synthetic sample exhibit ({name})", uploaded_by=user["username"]))
    return {"status": "SAMPLE_CASE_LOADED", "synthetic": True, "ingested": results}


@protected.post("/api/reset")
def reset_case_vault(confirm: str = "", user: Dict[str, Any] = Depends(require_admin)):
    """Demo helper. Clears case data but KEEPS the append-only audit log and records the reset in it."""
    if not ALLOW_RESET:
        raise HTTPException(403, "Reset is disabled in this environment (CHRONOFACT_ALLOW_RESET=false).")
    if confirm != "RESET":
        raise HTTPException(400, "Pass confirm=RESET to proceed. This deletes all exhibits from the vault.")
    with get_db() as conn:
        conn.execute("BEGIN IMMEDIATE")
        cur = conn.cursor()
        rows = [dict(r) for r in cur.execute("SELECT id, storage_path FROM evidence_items").fetchall()]
        for table in ("entity_mentions", "entities", "extracted_facts", "facts_fts", "inconsistencies", "evidence_items"):
            cur.execute(f"DELETE FROM {table}")
        append_audit_entry(cur, user["username"], "CASE_RESET", "CASE", "0" * 64, {"exhibits_removed": len(rows)})
    for r in rows:
        p = Path(r["storage_path"]).resolve()
        if p.parent == VAULT_DIR.resolve():
            p.unlink(missing_ok=True)
    return {"status": "SUCCESS", "message": "Case vault reset. Audit log preserved.", "exhibits_removed": len(rows)}


app.include_router(protected)
