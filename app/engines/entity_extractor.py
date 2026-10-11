"""
CHRONOFACT Dynamic Entity Extraction
=====================================
Extracts ALL IPs, Emails, URLs, Files without hardcoded assumptions.
"""

import re
from typing import Dict, List, Any


def extract_all_entities(text: str) -> Dict[str, List[str]]:
    """
    Dynamically extract entities from forensic text.
    No hardcoded city, country, or IP assumptions.
    """
    entities = {
        "ips": [],
        "emails": [],
        "urls": [],
        "files": [],
        "phone_numbers": [],
        "timestamps": [],
    }

    # 1. IPs (IPv4) - captures ANY valid IP, no whitelists
    ip_pattern = r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
    entities["ips"] = list(set(re.findall(ip_pattern, text)))

    # 2. Emails
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    entities["emails"] = list(set(re.findall(email_pattern, text)))

    # 3. URLs
    url_pattern = r"https?://[^\s/$.?#].[^\s]*"
    entities["urls"] = list(set(re.findall(url_pattern, text)))

    # 4. Files (common forensic formats)
    file_pattern = r"\b[\w\-\.]+\.(xlsx|xls|csv|txt|pdf|zip|eml|doc|docx|bin|jpg|jpeg|png|gif|mp4|avi|mov|psd|ppt|pptx)\b"
    entities["files"] = list(set(re.findall(file_pattern, text, re.IGNORECASE)))

    # 5. Phone Numbers (Universal format support)
    phone_pattern = r"(?:\+?\d{1,3}[-.\s]?)?\(?(?:\d{3})\)?[-.\s]?\d{3}[-.\s]?\d{4}"
    entities["phone_numbers"] = list(set(re.findall(phone_pattern, text)))

    # 6. ISO Timestamps
    time_pattern = r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?"
    entities["timestamps"] = list(set(re.findall(time_pattern, text)))

    return entities
