import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List
import uuid

def parse_csv_log_file(file_path: Path, evidence_id: str) -> Dict[str, Any]:
    """
    Parses CSV server authentication / audit / firewall logs.
    Format example: timestamp,user,ip_address,action,status
    Server logs with explicit UTC have high reliability and 0-width interval (t_min == t_max).
    """
    facts = []
    row_count = 0
    
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_count += 1
            # Normalize common column names
            timestamp_val = row.get("timestamp") or row.get("Date") or row.get("time") or ""
            user_val = row.get("user") or row.get("username") or row.get("account") or "Unknown"
            ip_val = row.get("ip_address") or row.get("ip") or row.get("source_ip") or ""
            action_val = row.get("action") or row.get("event") or row.get("description") or ""
            status_val = row.get("status") or row.get("result") or ""
            
            # Timestamp normalization
            t_min = "1970-01-01T00:00:00Z"
            t_max = "9999-12-31T23:59:59Z"
            tz_basis = "server_log_explicit_utc"
            
            if timestamp_val:
                try:
                    # Clean trailing Z
                    clean_ts = timestamp_val.replace("Z", "+00:00")
                    dt = datetime.fromisoformat(clean_ts)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    utc_iso = dt.astimezone(timezone.utc).isoformat()
                    t_min = utc_iso
                    t_max = utc_iso
                except Exception:
                    tz_basis = "unparsed_timestamp"
            
            raw_line = f"{timestamp_val},{user_val},{ip_val},{action_val},{status_val}"
            display_text = f"Timestamp: {timestamp_val} | User: {user_val} | IP: {ip_val} | Action: {action_val} | Status: {status_val}"
            fact_id = f"F-LOG-{uuid.uuid4().hex[:8]}"
            
            facts.append({
                "id": fact_id,
                "evidence_id": evidence_id,
                "fact_type": "SERVER_LOG_EVENT",
                "locator": f"CSV row {row_count}",
                "raw_text": raw_line,
                "display_text": display_text,
                "actor": user_val,
                "t_min": t_min,
                "t_max": t_max,
                "tz_basis": tz_basis,
                "time_reliability": "server_system_clock"
            })
            
    return {
        "total_rows": row_count,
        "facts": facts
    }
