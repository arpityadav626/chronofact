import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, List
import uuid

# Patterns for common chat formats:
# 1. iOS: [12/09/2025, 14:30:15] Alice: Message
# 2. Android: 12/09/2025, 2:30 pm - Alice: Message
# 3. ISO format: 2025-09-12 14:30:15 Alice: Message

CHAT_PATTERNS = [
    re.compile(r"^\[?(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[apAP][mM])?)\]?\s*(?:-\s*)?([^:]+):\s*(.*)$"),
    re.compile(r"^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+([^:]+):\s*(.*)$")
]

def parse_chat_file(file_path: Path, evidence_id: str) -> Dict[str, Any]:
    """
    Parses WhatsApp / text chat export files.
    Demonstrates uncertainty modeling: chat exports usually lack UTC offsets,
    so t_min and t_max are bounded intervals reflecting timezone ambiguity (e.g. UTC-12 to UTC+14).
    """
    facts = []
    line_number = 0
    
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line_number += 1
            line_clean = line.strip()
            if not line_clean:
                continue
                
            matched = False
            for pattern in CHAT_PATTERNS:
                m = pattern.match(line_clean)
                if m:
                    matched = True
                    groups = m.groups()
                    if len(groups) == 4:
                        date_str, time_str, sender, text = groups
                        # Try parsing flexible dates
                        dt = None
                        for fmt in ["%d/%m/%Y %H:%M:%S", "%d/%m/%Y %I:%M:%S %p", "%d/%m/%Y %I:%M %p", "%d/%m/%y %I:%M %p", "%d/%m/%y %H:%M"]:
                            try:
                                dt = datetime.strptime(f"{date_str} {time_str}", fmt)
                                break
                            except ValueError:
                                continue
                        if not dt:
                            dt = datetime(2025, 1, 1, 12, 0, 0)
                    else:
                        dt_str, sender, text = groups
                        try:
                            dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            dt = datetime(2025, 1, 1, 12, 0, 0)
                    
                    # Uncertainty Interval:
                    # Chat exports typically do NOT contain timezone information.
                    # We store nominal naive time and widen interval between UTC-12 and UTC+14 unless user confirms local TZ.
                    t_min = (dt - timedelta(hours=14)).replace(tzinfo=timezone.utc).isoformat()
                    t_max = (dt + timedelta(hours=12)).replace(tzinfo=timezone.utc).isoformat()
                    
                    fact_id = f"F-CHAT-{uuid.uuid4().hex[:8]}"
                    facts.append({
                        "id": fact_id,
                        "evidence_id": evidence_id,
                        "fact_type": "CHAT_MESSAGE",
                        "locator": f"Line {line_number}",
                        "raw_text": line_clean,
                        "actor": sender.strip(),
                        "t_min": t_min,
                        "t_max": t_max,
                        "tz_basis": "assumed_local_no_offset",
                        "time_reliability": "client_device_clock"
                    })
                    break

    return {
        "total_messages": len(facts),
        "facts": facts
    }
