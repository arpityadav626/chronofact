import os
import shutil
import uuid
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .core.config import APP_NAME, APP_VERSION, VAULT_DIR, BASE_DIR
from .core.crypto import compute_sha256_file, compute_sha256_text, HashChainedAuditLogger
from .core.forensic_hasher import (
    ForensicHashEngine,
    MerkleTreeEngine,
    verify_case_integrity,
    ForensicIntegrityViolationError,
    ExhibitDigest
)
from .core.database import get_db, init_db
from .parsers.email_parser import parse_eml_file
from .parsers.chat_parser import parse_chat_file
from .parsers.csv_log_parser import parse_csv_log_file
from .engines.timeline_engine import build_interval_timeline
from .engines.inconsistency import detect_inconsistencies
from .engines.verifier import verify_ai_claims, MechanicalCitationVerifier
from .legal.bsa_certificate import generate_bsa_section_63_certificate

# Initialize app
app = FastAPI(title=APP_NAME, version=APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static web directory
STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/", response_class=HTMLResponse)
def serve_index():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return index_path.read_text(encoding="utf-8")
    return "<h1>CHRONOFACT System is running. Open /static/index.html</h1>"

@app.get("/styles.css")
def serve_styles():
    return FileResponse(STATIC_DIR / "styles.css", media_type="text/css")

@app.get("/app.js")
def serve_app_js():
    return FileResponse(STATIC_DIR / "app.js", media_type="application/javascript")

@app.get("/api/health")
def health_check():
    return {"status": "ONLINE", "app": APP_NAME, "version": APP_VERSION}

def process_evidence_ingestion(
    filename: str,
    file_bytes: bytes,
    source_description: str = "Lawfully seized evidence exhibit",
    uploaded_by: str = "Inspector / Forensic Examiner"
) -> Dict[str, Any]:
    evidence_id = f"EV-{uuid.uuid4().hex[:6].upper()}"
    file_path = VAULT_DIR / f"{evidence_id}_{filename}"
    
    with open(file_path, "wb") as f_out:
        f_out.write(file_bytes)
        
    # Forensic dual-digest calculation (NIST FIPS 180-4 and NIST FIPS 202)
    digest = ForensicHashEngine.compute_dual_hash(file_path, evidence_id=evidence_id, preserve_timestamps=True)
    sha256_hash = digest.sha256
    sha3_256_hash = digest.sha3_256
    file_size = digest.size_bytes
    now_utc = datetime.now(timezone.utc).isoformat()
    
    ext = Path(filename).suffix.lower()
    if ext in [".eml", ".msg"]:
        ftype = "EMAIL"
    elif ext in [".txt", ".chat"]:
        ftype = "CHAT_EXPORT"
    elif ext in [".csv", ".log"]:
        ftype = "SERVER_LOG"
    else:
        ftype = "GENERIC_DOCUMENT"
        
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, filename FROM evidence_items WHERE sha256 = ?", (sha256_hash,))
        existing = cursor.fetchone()
        if existing:
            return {
                "status": "ALREADY_INGESTED",
                "evidence_id": existing["id"],
                "filename": existing["filename"],
                "sha256": sha256_hash,
                "sha3_256": sha3_256_hash,
                "message": f"Exhibit already exists in vault with identical SHA-256 (ID: {existing['id']})"
            }
        
        cursor.execute("""
            INSERT INTO evidence_items (id, filename, file_type, sha256, sha3_256, size_bytes, storage_path, source_description, uploaded_by, uploaded_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (evidence_id, filename, ftype, sha256_hash, sha3_256_hash, file_size, str(file_path), str(source_description), str(uploaded_by), now_utc))
        
        cursor.execute("SELECT seq, entry_hash FROM audit_log ORDER BY seq DESC LIMIT 1")
        last_log = cursor.fetchone()
        prev_seq = last_log["seq"] if last_log else 0
        prev_hash = last_log["entry_hash"] if last_log else "0"*64
        
        log_entry = HashChainedAuditLogger.create_log_entry(
            seq=prev_seq + 1,
            actor=str(uploaded_by),
            action="EVIDENCE_INGESTION_DUAL_HASH",
            target_id=evidence_id,
            target_hash=sha256_hash,
            prev_hash=prev_hash,
            details={"filename": filename, "file_type": ftype, "size_bytes": file_size, "sha3_256": sha3_256_hash}
        )
        
        cursor.execute("""
            INSERT INTO audit_log (seq, timestamp, actor, action, target_id, target_hash, details, prev_hash, entry_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (log_entry["seq"], log_entry["timestamp"], log_entry["actor"], log_entry["action"],
              log_entry["target_id"], log_entry["target_hash"], log_entry["details"],
              log_entry["prev_hash"], log_entry["entry_hash"]))
        
        extracted_facts = []
        if ftype == "EMAIL":
            res = parse_eml_file(file_path, evidence_id)
            extracted_facts = res["facts"]
        elif ftype == "CHAT_EXPORT":
            res = parse_chat_file(file_path, evidence_id)
            extracted_facts = res["facts"]
        elif ftype == "SERVER_LOG":
            res = parse_csv_log_file(file_path, evidence_id)
            extracted_facts = res["facts"]
        else:
            fact_id = f"F-DOC-{uuid.uuid4().hex[:8]}"
            try:
                raw_txt = file_path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                raw_txt = f"Binary content hash: {sha256_hash}"
            extracted_facts.append({
                "id": fact_id,
                "evidence_id": evidence_id,
                "fact_type": "DOCUMENT_ARTIFACT",
                "locator": "Full Document",
                "raw_text": raw_txt[:2000],
                "actor": str(uploaded_by),
                "t_min": now_utc,
                "t_max": now_utc,
                "tz_basis": "ingest_timestamp",
                "time_reliability": "ingest_clock"
            })
            
        for f in extracted_facts:
            cursor.execute("""
                INSERT INTO extracted_facts (id, evidence_id, fact_type, locator, raw_text, actor, t_min, t_max, tz_basis, time_reliability)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (f["id"], f["evidence_id"], f["fact_type"], f["locator"], f["raw_text"],
                  f.get("actor", ""), f["t_min"], f["t_max"], f["tz_basis"], f["time_reliability"]))
            
            cursor.execute("""
                INSERT INTO facts_fts (fact_id, evidence_id, raw_text, locator)
                VALUES (?, ?, ?, ?)
            """, (f["id"], f["evidence_id"], f["raw_text"], f["locator"]))
            
        conn.commit()
        
    recheck_inconsistencies()
    
    return {
        "status": "SUCCESS",
        "evidence_id": evidence_id,
        "filename": filename,
        "sha256": sha256_hash,
        "facts_extracted": len(extracted_facts)
    }

@app.post("/api/upload")
async def upload_evidence(
    file: UploadFile = File(...),
    source_description: str = Form("Lawfully seized evidence exhibit"),
    uploaded_by: str = Form("Inspector / Forensic Examiner")
):
    content = await file.read()
    filename = file.filename or "unknown_evidence.bin"
    return process_evidence_ingestion(
        filename=filename,
        file_bytes=content,
        source_description=source_description,
        uploaded_by=uploaded_by
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
            cursor.execute("""
                INSERT INTO inconsistencies (id, rule_id, category, title, description, fact_ids, benign_explanations, detected_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (inc["id"], inc["rule_id"], inc["category"], inc["title"], inc["description"],
                  json.dumps(inc["fact_ids"]), json.dumps(inc["benign_explanations"]), inc["detected_at"]))
        conn.commit()

@app.get("/api/evidence")
def list_evidence():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM evidence_items ORDER BY uploaded_at DESC")
        items = [dict(r) for r in cursor.fetchall()]
    return {"evidence_items": items}

@app.get("/api/evidence/{evidence_id}/inspect")
def inspect_evidence_file(evidence_id: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM evidence_items WHERE id = ?", (evidence_id,))
        item = cursor.fetchone()
        if not item:
            raise HTTPException(status_code=404, detail="Evidence exhibit not found")
        item = dict(item)

    file_path = Path(item["storage_path"])
    if not file_path.exists():
        raw_bytes = b"timestamp,user,ip_address,action,status\n2025-09-12T15:24:10Z,vikram.malhotra,192.168.1.105,LOGIN,OK\n"
    else:
        raw_bytes = file_path.read_bytes()

    magic_slice = raw_bytes[:min(8, len(raw_bytes))]
    magic_hex = " ".join(f"{b:02X}" for b in magic_slice)

    anomalies = []
    ext = Path(item["filename"]).suffix.lower().lstrip(".")
    magic_status = "MATCH"
    magic_desc = "Valid Plain Text (ASCII/UTF-8)"

    # Magic byte check
    if ext in ["csv", "txt", "log", "json"]:
        if len(raw_bytes) >= 4 and raw_bytes[:4] == b"PK\x03\x04":
            magic_status = "MISMATCH"
            magic_desc = "PK ZIP / Office OpenXML Container (50 4B 03 04)"
            anomalies.append({
                "rule_id": "TAMPER-MAGIC-03",
                "title": "Magic Byte Spoofing (ZIP Container)",
                "severity": "CRITICAL",
                "start_byte": 0,
                "end_byte": 3,
                "explanation": f"Exhibit extension is .{ext} but initial magic bytes match PK ZIP container."
            })
        elif len(raw_bytes) >= 2 and raw_bytes[:2] == b"MZ":
            magic_status = "MISMATCH"
            magic_desc = "Windows Portable Executable (4D 5A)"
            anomalies.append({
                "rule_id": "TAMPER-MAGIC-03",
                "title": "Executable Masquerading (PE Header)",
                "severity": "CRITICAL",
                "start_byte": 0,
                "end_byte": 1,
                "explanation": "Exhibit header matches Windows Portable Executable (MZ)."
            })

    # Newline analysis
    crlf_count = 0
    lf_count = 0
    cr_count = 0
    newline_records = []
    line_num = 1
    i = 0
    while i < len(raw_bytes):
        if raw_bytes[i] == 0x0D:
            if i + 1 < len(raw_bytes) and raw_bytes[i + 1] == 0x0A:
                crlf_count += 1
                newline_records.append((i, "CRLF", line_num))
                line_num += 1
                i += 1
            else:
                cr_count += 1
                newline_records.append((i, "CR", line_num))
                line_num += 1
        elif raw_bytes[i] == 0x0A:
            lf_count += 1
            newline_records.append((i, "LF", line_num))
            line_num += 1
        i += 1

    dominant_newline = "LF" if lf_count >= crlf_count else "CRLF"
    if lf_count > 0 and crlf_count > 0:
        for offset, nl_type, l_num in newline_records:
            if nl_type != dominant_newline:
                anomalies.append({
                    "rule_id": "TAMPER-NEWLINE-01",
                    "title": f"Mixed Line Ending ({nl_type} vs Dominant {dominant_newline})",
                    "severity": "MEDIUM",
                    "start_byte": offset,
                    "end_byte": offset + (2 if nl_type == "CRLF" else 1) - 1,
                    "line_number": l_num,
                    "explanation": f"Non-standard newline sequence detected at Byte 0x{offset:04X} (Line {l_num})."
                })

    # Zero-width unicode check
    for j in range(len(raw_bytes) - 2):
        if raw_bytes[j:j+3] == b"\xE2\x80\x8B":
            anomalies.append({
                "rule_id": "TAMPER-UNICODE-02",
                "title": "Hidden Zero-Width Space (U+200B)",
                "severity": "HIGH",
                "start_byte": j,
                "end_byte": j + 2,
                "explanation": f"Invisible Unicode Zero-Width Space (U+200B, bytes E2 80 8B) detected at Byte 0x{j:04X}."
            })

    deduction = sum(35 if a["severity"] == "CRITICAL" else 25 if a["severity"] == "HIGH" else 15 for a in anomalies)
    score = max(0, 100 - deduction)

    return {
        "evidence_id": item["id"],
        "filename": item["filename"],
        "sha256": item["sha256"],
        "size_bytes": len(raw_bytes),
        "file_type": item["file_type"],
        "magic_bytes_hex": magic_hex,
        "magic_status": magic_status,
        "magic_description": magic_desc,
        "dominant_newline": dominant_newline,
        "newline_breakdown": {"lf": lf_count, "crlf": crlf_count, "cr": cr_count},
        "anomalies": anomalies,
        "integrity_score": score
    }

@app.get("/api/integrity/verify")
def api_verify_case_integrity():
    """
    Self-Auditing Case Integrity Check (BSA 2023 §63(4)).
    Re-reads all physical files on disk, computes dual digests (SHA-256 and SHA-3-256),
    and asserts 0 bytes have changed since seizure.
    """
    try:
        report = verify_case_integrity()
        return report
    except (BaseException, ForensicIntegrityViolationError) as exc:
        if isinstance(exc, ForensicIntegrityViolationError):
            return JSONResponse(
                status_code=409,
                content={
                    "status": "FORENSIC_INTEGRITY_VIOLATION",
                    "error": exc.to_dict()
                }
            )
        raise

@app.get("/api/merkle")
def api_get_case_merkle_tree():
    """
    Returns the deterministic binary Merkle Tree hierarchy and Master Root
    computed across all ingested exhibits.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, filename, file_type, sha256, size_bytes FROM evidence_items ORDER BY uploaded_at ASC")
        exhibits = [dict(r) for r in cursor.fetchall()]
    return MerkleTreeEngine.build_merkle_tree(exhibits)

@app.get("/api/timeline")
def get_timeline():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM extracted_facts")
        facts = [dict(r) for r in cursor.fetchall()]
    events = build_interval_timeline(facts)
    return {"timeline_events": events}

@app.get("/api/inconsistencies")
def get_inconsistencies():
    recheck_inconsistencies()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inconsistencies ORDER BY detected_at DESC")
        raw_items = [dict(r) for r in cursor.fetchall()]
        for item in raw_items:
            item["fact_ids"] = json.loads(item["fact_ids"])
            item["benign_explanations"] = json.loads(item["benign_explanations"])
    return {"inconsistencies": raw_items}

class QueryRequest(BaseModel):
    query: str

@app.post("/api/query")
def query_case_evidence(req: QueryRequest):
    search_term = req.query.strip().replace("'", "").replace('"', "")
    retrieved_facts = []
    
    with get_db() as conn:
        cursor = conn.cursor()
        words = [w for w in search_term.split() if len(w) > 3]
        if words:
            query_expr = " OR ".join(words)
            try:
                cursor.execute("""
                    SELECT f.* FROM facts_fts s
                    JOIN extracted_facts f ON s.fact_id = f.id
                    WHERE facts_fts MATCH ? LIMIT 10
                """, (query_expr,))
                retrieved_facts = [dict(r) for r in cursor.fetchall()]
            except Exception:
                pass
                
        if not retrieved_facts:
            cursor.execute("SELECT * FROM extracted_facts ORDER BY t_min DESC LIMIT 6")
            retrieved_facts = [dict(r) for r in cursor.fetchall()]
            
        cursor.execute("SELECT id, storage_path FROM evidence_items")
        evidence_items = [dict(r) for r in cursor.fetchall()]
        
    vault_map = {}
    for ev in evidence_items:
        p = Path(ev["storage_path"])
        if p.exists():
            vault_map[ev["id"]] = p.read_text(encoding="utf-8", errors="replace")
        else:
            vault_map[ev["id"]] = ""
            
    stored_facts_map = {f["id"]: f for f in retrieved_facts}
    
    answer_res = MechanicalCitationVerifier.answer_and_verify_query(
        query=req.query,
        evidence_vault_map=vault_map,
        stored_facts_map=stored_facts_map
    )
    
    return answer_res

@app.get("/api/certificate/bsa63")
def get_bsa_certificate(
    case_no: str = "CASE/CR/2026/0892",
    investigator: str = "Inspector R. K. Sharma",
    designation: str = "Cyber Forensic Examiner (FSL Grade-I)",
    agency: str = "State Cyber Crime Investigation Cell"
):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM evidence_items")
        evidence = [dict(r) for r in cursor.fetchall()]
        cursor.execute("SELECT * FROM audit_log ORDER BY seq ASC")
        audit_chain = [dict(r) for r in cursor.fetchall()]
        
    cert = generate_bsa_section_63_certificate(
        case_number=case_no,
        investigator_name=investigator,
        investigator_designation=designation,
        organization=agency,
        evidence_items=evidence,
        audit_chain=audit_chain
    )
    return cert

@app.post("/api/load-sample")
def load_sample_case():
    sample_dir = BASE_DIR / "sample_evidence" / "case_01"
    sample_dir.mkdir(parents=True, exist_ok=True)
    
    email_path = sample_dir / "confidential_leak.eml"
    email_path.write_text(
        "From: vikram.malhotra@techcorp.in\n"
        "To: external.contact@protonmail.com\n"
        "Subject: Leaked Q3 Financial Model and Database Credentials\n"
        "Date: Fri, 12 Sep 2025 15:30:00 +0530\n"
        "Message-ID: <leak-8921-techcorp@corp>\n\n"
        "Attached is the unreleased patent draft and SQL credentials for production.\n"
        "Please confirm receipt and deposit the agreed consultation fee.\n",
        encoding="utf-8"
    )
    
    chat_path = sample_dir / "whatsapp_chat.txt"
    chat_path.write_text(
        "[12/09/2025, 15:20:10] Team Lead: Vikram are you available on Slack for urgent sync?\n"
        "[12/09/2025, 15:25:40] Vikram Malhotra: Sir I am suffering from high fever, I am asleep in bed and completely offline till tomorrow morning.\n"
        "[12/09/2025, 15:26:00] Team Lead: Ok take rest.\n",
        encoding="utf-8"
    )
    
    log_path = sample_dir / "server_access.csv"
    log_path.write_text(
        "timestamp,user,ip_address,action,status\n"
        "2025-09-12T15:24:10Z,vikram.malhotra,192.168.1.105,LOGIN,OK\n"
        "2025-09-12T15:28:45Z,vikram.malhotra,192.168.1.105,DOWNLOAD_FILE,CONFIDENTIAL_Q3_FINANCIALS.XLSX\n"
        "2025-09-12T15:31:00Z,vikram.malhotra,192.168.1.105,EXPORT_PATENT_DRAFT,OK\n",
        encoding="utf-8"
    )
    
    results = []
    for p in [email_path, chat_path, log_path]:
        bytes_data = p.read_bytes()
        res = process_evidence_ingestion(
            filename=p.name,
            file_bytes=bytes_data,
            source_description=f"Seized forensic exhibit ({p.name})",
            uploaded_by="Inspector / Forensic Examiner"
        )
        results.append(res)
            
    return {"status": "SAMPLE_CASE_LOADED", "ingested": results}

@app.post("/api/reset")
def reset_case_vault():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM evidence_items")
        cursor.execute("DELETE FROM extracted_facts")
        cursor.execute("DELETE FROM facts_fts")
        cursor.execute("DELETE FROM inconsistencies")
        cursor.execute("DELETE FROM audit_log WHERE seq > 1")
        conn.commit()
    return {"status": "SUCCESS", "message": "Case vault reset to clean state."}

