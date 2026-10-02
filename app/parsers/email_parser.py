import email
from email import policy
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, List
import uuid

def parse_eml_file(file_path: Path, evidence_id: str) -> Dict[str, Any]:
    """
    Parses an RFC 822 / MIME .eml email file.
    Extracts headers, body text, received hops, and creates interval timestamps.
    """
    with open(file_path, "rb") as f:
        msg = email.message_from_binary_file(f, policy=policy.default)
        
    date_header = msg.get("Date")
    from_header = msg.get("From", "")
    to_header = msg.get("To", "")
    subject_header = msg.get("Subject", "")
    message_id = msg.get("Message-ID", "")
    
    # Process timestamp & determine interval
    tz_basis = "explicit_offset"
    reliability = "server_and_client_headers"
    
    if date_header:
        try:
            dt = parsedate_to_datetime(date_header)
            # Normalize to UTC
            utc_dt = dt.astimezone(timezone.utc)
            t_min = utc_dt.isoformat()
            t_max = utc_dt.isoformat()
        except Exception:
            # Fallback if unparseable date
            t_min = "1970-01-01T00:00:00Z"
            t_max = "9999-12-31T23:59:59Z"
            tz_basis = "unparseable_date"
    else:
        t_min = "1970-01-01T00:00:00Z"
        t_max = "9999-12-31T23:59:59Z"
        tz_basis = "missing_date"

    # Extract plain text body
    body_text = ""
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get("Content-Disposition"))
            if ctype == "text/plain" and "attachment" not in cdispo:
                body_text += part.get_payload(decode=True).decode(errors="replace") + "\n"
    else:
        body_text = msg.get_payload(decode=True).decode(errors="replace")

    # Received chain (vital for spoofing & skew detection)
    received_headers = msg.get_all("Received", [])
    
    facts = []
    # Primary email fact
    fact_id = f"F-EML-{uuid.uuid4().hex[:8]}"
    summary_text = f"Email from '{from_header}' to '{to_header}' | Subject: '{subject_header}' | Body: {body_text.strip()[:300]}"
    
    facts.append({
        "id": fact_id,
        "evidence_id": evidence_id,
        "fact_type": "EMAIL_MESSAGE",
        "locator": f"Message-ID: {message_id}",
        "raw_text": f"From: {from_header}\nTo: {to_header}\nSubject: {subject_header}\nDate: {date_header}\n\n{body_text.strip()}",
        "actor": from_header,
        "t_min": t_min,
        "t_max": t_max,
        "tz_basis": tz_basis,
        "time_reliability": reliability
    })

    return {
        "headers": {
            "Date": date_header,
            "From": from_header,
            "To": to_header,
            "Subject": subject_header,
            "Message-ID": message_id,
            "Received_Count": len(received_headers)
        },
        "facts": facts,
        "raw_body": body_text
    }
