"""
CHRONOFACT Module 2: Cross-Modal Inconsistency & Alibi Conflict Radar
====================================================================
Compliant with:
- Gunestas et al. (IoI Digital Forensic Consistency Framework, Sept 2026)
- Haversine Geospatial Geodesic Distance & Velocity Impossibility
- Mandatory Multi-Hypothesis Benign Explanation Generator (BSA 2023 §63(4))

Author: Arpit Yadav & Team (SUTRAM 2026 // Cyber Forensic Research)
"""

import os
import re
import math
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Tuple

from .timeline_engine import parse_iso_datetime, format_utc_and_ist, IST_OFFSET


def _parse_offset_minutes(text: str) -> int:
    m = re.fullmatch(r"\s*([+-])(\d{1,2}):?(\d{2})\s*", text or "")
    if not m:
        return 330
    sign = -1 if m.group(1) == "-" else 1
    return sign * (int(m.group(2)) * 60 + int(m.group(3)))


# Chat exports carry no UTC offset. The parser therefore stores a 26-hour uncertainty interval
# [wall_clock - 14h, wall_clock + 12h]. Correlation rules need ONE reference instant; we use an explicit,
# configurable assumption (default IST, +05:30, for Indian investigations) and always disclose it.
ASSUMED_CHAT_TZ = os.getenv("CHRONOFACT_ASSUMED_CHAT_TZ", "+05:30")
ASSUMED_CHAT_OFFSET_MIN = _parse_offset_minutes(ASSUMED_CHAT_TZ)
ALIBI_CLOCK_SKEW_TOLERANCE_SEC = 60  # events up to 60 s before the statement still count (device clock skew)


def chat_reference_instant(fact: Dict[str, Any]) -> Optional[datetime]:
    """Best single instant (UTC) for a fact. For offset-less chat facts, recover the wall-clock time from the
    interval lower bound (wall - 14h) and apply the assumed zone. The old rules used the raw lower bound, which is
    up to 14 hours before any realistic reading and made the alibi rule miss real contradictions."""
    t_min = parse_iso_datetime(fact.get("t_min") or "")
    if not t_min:
        return None
    if fact.get("tz_basis") != "assumed_local_no_offset":
        return t_min
    wall = (t_min + timedelta(hours=14)).replace(tzinfo=None)
    return (wall - timedelta(minutes=ASSUMED_CHAT_OFFSET_MIN)).replace(tzinfo=timezone.utc)


# ==============================================================================
# GEODETIC HAVERSINE VELOCITY CALCULATOR (PHYSICAL IMPOSSIBILITY)
# ==============================================================================

def calculate_haversine_distance_km(
    lat1: float, lon1: float,
    lat2: float, lon2: float
) -> float:
    """
    Computes great-circle distance between two geographic coordinates using the Haversine formula.
    Returns distance in kilometers.
    """
    R = 6371.0  # Earth's mean radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


# Common investigative coordinate references (India)
LOCATION_COORDINATES: Dict[str, Tuple[float, float]] = {
    "delhi": (28.6139, 77.2090),
    "mumbai": (19.0760, 72.8777),
    "bangalore": (12.9716, 77.5946),
    "hyderabad": (17.3850, 78.4867),
    "pune": (18.5204, 73.8567),
    "noida": (28.5355, 77.3910),
    "gurugram": (28.4595, 77.0266)
}


# ==============================================================================
# DETERMINISTIC INCONSISTENCY RADAR ENGINE
# ==============================================================================

class InconsistencyRadarEngine:
    """
    Deterministic Inconsistency and Contradiction Detection Engine.
    
    Principles:
    1. Cross-Modal Evidence Synthesis: Correlates natural language witness/suspect statements
       against machine-generated log telemetry (auth logs, email headers, carrier CDRs).
    2. Confirmation Bias Countermeasure: In digital forensic jurisprudence (BSA 2023 §63(4)),
       the defense often alleges innocent technological anomalies. Every flagged inconsistency
       MUST algorithmically attach concrete, plausible benign explanations.
    """

    @classmethod
    def detect_all_inconsistencies(
        cls,
        facts: List[Dict[str, Any]],
        evidence_items: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Executes all forensic inconsistency rules across ingested facts and exhibits.
        """
        inconsistencies: List[Dict[str, Any]] = []

        # Partition facts by modality
        chat_facts = [f for f in facts if f.get("fact_type") in ["CHAT_MESSAGE", "CHAT_EXPORT"]]
        log_facts = [f for f in facts if f.get("fact_type") in ["SERVER_LOG_EVENT", "SERVER_LOG", "AUTH_EVENT", "FILE_TRANSFER"]]
        email_facts = [f for f in facts if f.get("fact_type") in ["EMAIL_MESSAGE", "EMAIL"]]

        # Rule 1: Alibi Claim vs Server Reality (Temporal / Behavioral Contradiction)
        inconsistencies.extend(cls._detect_alibi_server_contradictions(chat_facts, log_facts))

        # Rule 2: Geographic & Velocity Impossibility (Impossible Travel Speed)
        inconsistencies.extend(cls._detect_geographic_impossibility(chat_facts, log_facts))

        # Rule 3: Document Post-Transmission Modification (Causal Inversion)
        inconsistencies.extend(cls._detect_post_transmission_modifications(email_facts, log_facts))

        # Rule 4: Cryptographic Duplicate Renaming (Structural Tampering)
        inconsistencies.extend(cls._detect_cryptographic_duplicates(evidence_items))

        # Rule 5: Timezone Spoofing & Clock Inversion
        inconsistencies.extend(cls._detect_timezone_clock_spoofing(email_facts, chat_facts))

        return inconsistencies

    # --------------------------------------------------------------------------
    # RULE 1: ALIBI STATEMENT VS SERVER TELEMETRY
    # --------------------------------------------------------------------------
    @classmethod
    def _detect_alibi_server_contradictions(
        cls,
        chat_facts: List[Dict[str, Any]],
        log_facts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        anomalies = []
        alibi_patterns = [
            r"\b(asleep|sleeping|sleep|so raha|soya)\b",
            r"\b(offline|airplane mode|flight mode|switched off|phone off)\b",
            r"\b(fever|sick|hospital|bed rest|headache|ill)\b",
            r"\b(away from laptop|not at desk|away from system)\b"
        ]

        for chat in chat_facts:
            text = (chat.get("raw_text") or chat.get("content") or "").lower()
            matched_alibi = any(re.search(pat, text, re.IGNORECASE) for pat in alibi_patterns)
            if not matched_alibi:
                continue

            chat_dt = chat_reference_instant(chat)
            if not chat_dt:
                continue

            # Look for concurrent or subsequent server logins/downloads within 12 hours
            for log in sorted(log_facts, key=lambda l: l.get("t_min") or ""):
                log_text = (log.get("raw_text") or log.get("content") or "")
                log_dt = parse_iso_datetime(log.get("t_min") or "")
                if not log_dt:
                    continue

                # A "I'm asleep/offline" statement is forward-looking: only activity AFTER it contradicts it.
                # (The old window started 30 minutes BEFORE the statement, so a normal login just before
                # someone says "going to sleep" was reported as a CRITICAL contradiction.)
                time_diff_sec = (log_dt - chat_dt).total_seconds()
                if -ALIBI_CLOCK_SKEW_TOLERANCE_SEC <= time_diff_sec <= 43200:
                    # Check if action is an active user operation
                    if any(term in log_text.upper() for term in ["LOGIN", "DOWNLOAD", "EXPORT", "SSH", "SESSION", "TRANSFER"]):
                        inc_id = f"INC-TMP-{uuid.uuid4().hex[:6].upper()}"
                        
                        # Calculate human discrepancy delta
                        hrs = int(abs(time_diff_sec) // 3600)
                        mins = int((abs(time_diff_sec) % 3600) // 60)
                        delta_str = (
                            f"Active server session authenticated {hrs}h {mins}m "
                            f"{'after' if time_diff_sec >= 0 else 'before'} claimed sleep statement."
                        )

                        # Extract dynamic log fields
                        ip_match = re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", log_text)
                        ip = ip_match.group(0) if ip_match else "Assigned Network Endpoint"
                        
                        user = log.get("actor")
                        if not user or user == "System":
                            # Try parsing username from CSV or log text
                            parts = [p.strip() for p in log_text.split(",")]
                            if len(parts) >= 2 and "@" in parts[1] or "." in parts[1]:
                                user = parts[1]
                            else:
                                user = "Authenticated Subject"

                        # Extract action
                        action_match = re.search(r"\b(LOGIN|DOWNLOAD_FILE|EXPORT_PATENT_DRAFT|EXPORT|SSH|SESSION|TRANSFER)\b", log_text.upper())
                        action = action_match.group(0) if action_match else "SYSTEM_OPERATION"

                        chat_ist = format_utc_and_ist(chat_dt)["ist_display"]
                        log_ist = format_utc_and_ist(log_dt)["ist_display"]

                        anomalies.append({
                            "id": inc_id,
                            "rule_id": "RULE_ALIBI_VS_SERVER_LOG",
                            "category": "Alibi Inconsistency",
                            "severity": "CRITICAL",
                            "title": "Temporal Contradiction: Suspect active during claimed sleep/offline period",
                            "description": (
                                f"Statement ({chat.get('locator', 'Record')}) records subject claiming: '{chat.get('raw_text')}'. "
                                f"However, Server Telemetry ({log.get('locator', 'Log Record')}) records active operation "
                                f"for '{user}' from IP {ip} ({action}) at {log_ist}."
                            ),
                            "discrepancy_delta": delta_str,
                            "timezone_assumption": (
                                f"Chat timestamp has no UTC offset; {ASSUMED_CHAT_TZ} assumed "
                                f"(override with CHRONOFACT_ASSUMED_CHAT_TZ). Confirm the device timezone before relying on this gap."
                                if chat.get("tz_basis") == "assumed_local_no_offset" else "Explicit offsets on both sources."
                            ),
                            "fact_ids": [chat["id"], log["id"]],
                            "claimed_statement": {
                                "source": f"{chat.get('fact_type', 'COMMUNICATION')} • {chat.get('locator', 'Ref')}",
                                "text": chat.get("raw_text") or "",
                                "timestamp_ist": chat_ist,
                                "timestamp_utc": chat_dt.isoformat()
                            },
                            "server_reality": {
                                "source": f"Telemetry • {log.get('locator', 'Log')}",
                                "action": action,
                                "user": user,
                                "ip": ip,
                                "timestamp_ist": log_ist,
                                "timestamp_utc": log_dt.isoformat()
                            },
                            "benign_explanations": [
                                "Automated cron batch background task or daemon authenticated under user's API key without keyboard interaction.",
                                "Shared credentials across family member, domestic staff, or organizational colleague.",
                                "Device local hardware clock unsynchronized (client was set to non-NTP time offset).",
                                "Colloquial conversational use of 'going to sleep' or 'offline' prior to actual system sign-off."
                            ],
                            "detected_at": datetime.now(timezone.utc).isoformat()
                        })
                        break  # Limit 1 major alibi conflict per chat fact to avoid noise

        return anomalies

    # --------------------------------------------------------------------------
    # RULE 2: GEOGRAPHIC & VELOCITY IMPOSSIBILITY (HAVERSINE KINEMATICS)
    # --------------------------------------------------------------------------
    @classmethod
    def _detect_geographic_impossibility(
        cls,
        chat_facts: List[Dict[str, Any]],
        log_facts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Detects physical impossibility when two distinct geographic locations are claimed
        or recorded within a time delta that would require physically impossible transit speeds (> 800 km/h).
        Evaluates both natural language claims and cellular CDR tower telemetry coordinates.
        """
        anomalies = []
        
        # Helper to extract real locations or CDR coordinates
        def extract_known_location(fact: Dict[str, Any]) -> Optional[Tuple[str, Tuple[float, float]]]:
            text = (fact.get("raw_text") or "") + " " + (fact.get("display_text") or "")
            text_lower = text.lower()

            # 1. Direct geodetic coordinates from TELECOM_CDR telemetry
            lat_m = re.search(r"(?:latitude|lat)[:=]?\s*([+-]?\d+\.\d+)", text_lower)
            lon_m = re.search(r"(?:longitude|lon)[:=]?\s*([+-]?\d+\.\d+)", text_lower)
            if lat_m and lon_m:
                try:
                    lat, lon = float(lat_m.group(1)), float(lon_m.group(1))
                    tower_m = re.search(r"(?:cell_tower_id|tower)[:=]?\s*([A-Za-z0-9_\-]+)", text, re.IGNORECASE)
                    tower_label = f"Tower {tower_m.group(1)}" if tower_m else f"Cell ({lat:.4f}, {lon:.4f})"
                    return tower_label, (lat, lon)
                except (ValueError, TypeError):
                    pass

            # 2. Known city entities in text
            for city_name, coords in LOCATION_COORDINATES.items():
                if re.search(r"\b" + re.escape(city_name) + r"\b", text_lower):
                    return city_name.title(), coords
            return None

        # Build list of all location-bearing events
        loc_events = []
        for chat in chat_facts:
            loc = extract_known_location(chat)
            dt = chat_reference_instant(chat)
            if loc and dt:
                loc_events.append({"fact": chat, "loc_name": loc[0], "coords": loc[1], "dt": dt, "type": "STATEMENT"})

        for log in log_facts:
            loc = extract_known_location(log)
            dt = parse_iso_datetime(log.get("t_min") or "")
            if loc and dt:
                loc_events.append({"fact": log, "loc_name": loc[0], "coords": loc[1], "dt": dt, "type": "TELEMETRY"})

        # Compare pairs sorted by time
        loc_events.sort(key=lambda x: x["dt"])
        for i in range(len(loc_events)):
            for j in range(i + 1, len(loc_events)):
                e1, e2 = loc_events[i], loc_events[j]
                # Avoid comparing two identical locations
                if e1["loc_name"] == e2["loc_name"]:
                    continue

                time_diff_hours = (e2["dt"] - e1["dt"]).total_seconds() / 3600.0
                if 0.001 <= time_diff_hours <= 2.0:  # Under 2 hours window
                    dist_km = calculate_haversine_distance_km(
                        e1["coords"][0], e1["coords"][1],
                        e2["coords"][0], e2["coords"][1]
                    )
                    velocity_kmh = dist_km / max(0.01, time_diff_hours)

                    # Commercial flight cruise speed ~ 850 km/h; supersonic > 850 km/h is impossible for civilians
                    if velocity_kmh > 800.0 and dist_km > 50.0:
                        inc_id = f"INC-GEO-{uuid.uuid4().hex[:6].upper()}"
                        anomalies.append({
                            "id": inc_id,
                            "rule_id": "RULE_GEOGRAPHIC_IMPOSSIBILITY",
                            "category": "Geospatial Velocity Impossibility",
                            "severity": "CRITICAL",
                            "title": f"Geographic Impossibility Flag: Physical location mismatch ({int(dist_km)} km)",
                            "description": (
                                f"Subject was recorded at {e1['loc_name']} at {format_utc_and_ist(e1['dt'])['ist_display']}, "
                                f"yet {e2['type'].lower()} places activity at {e2['loc_name']} "
                                f"{int(time_diff_hours * 60)} minutes later. Required physical transit speed: {int(velocity_kmh)} km/h."
                            ),
                            "discrepancy_delta": f"Distance {int(dist_km)} km in {int(time_diff_hours * 60)} min (Implied Velocity: {int(velocity_kmh)} km/h - Physically Impossible).",
                            "fact_ids": [e1["fact"]["id"], e2["fact"]["id"]],
                            "geo_telemetry": {
                                "claimed_location": {"city": e1["loc_name"], "lat": e1["coords"][0], "lon": e1["coords"][1]},
                                "network_location": {"city": e2["loc_name"], "lat": e2["coords"][0], "lon": e2["coords"][1]},
                                "distance_km": round(dist_km, 1),
                                "transit_hours": round(time_diff_hours, 2),
                                "required_speed_kmh": round(velocity_kmh, 1)
                            },
                            "benign_explanations": [
                                "Virtual Private Network (VPN) or corporate proxy exit node located in different geographic telecom zone.",
                                "Cell tower antenna signal bounce / carrier network Address Translation (CGNAT) gateway misattribution.",
                                "Remote Desktop Protocol (RDP) or TeamViewer session initiated from another authorized team member.",
                                "Carrier CDR handover latency between cellular Base Transceiver Stations (BTS)."
                            ],
                            "detected_at": datetime.now(timezone.utc).isoformat()
                        })
                        break

        return anomalies

    # --------------------------------------------------------------------------
    # RULE 3: POST-TRANSMISSION DOCUMENT MODIFICATION (CAUSAL INVERSION)
    # --------------------------------------------------------------------------
    @classmethod
    def _detect_post_transmission_modifications(
        cls,
        email_facts: List[Dict[str, Any]],
        log_facts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        anomalies = []

        for eml in email_facts:
            eml_dt = parse_iso_datetime(eml.get("t_min") or "")
            if not eml_dt:
                continue

            for log in log_facts:
                log_dt = parse_iso_datetime(log.get("t_min") or "")
                if not log_dt:
                    continue

                log_text = log.get("raw_text", "").upper()
                if any(act in log_text for act in ["EXPORT", "DOWNLOAD", "MODIFIED", "SAVE"]) and log_dt > eml_dt:
                    if any(term in log_text for term in ["PATENT", "FINANCIAL", "DRAFT", "CREDENTIAL"]):
                        diff_sec = (log_dt - eml_dt).total_seconds()
                        if 0 < diff_sec <= 86400:  # Within 24 hours
                            inc_id = f"INC-CSL-{uuid.uuid4().hex[:6].upper()}"
                            mins = int(diff_sec // 60)
                            anomalies.append({
                                "id": inc_id,
                                "rule_id": "RULE_CAUSAL_INVERSION_POST_TRANSMISSION",
                                "category": "Causal Sequence Inversion",
                                "severity": "HIGH",
                                "title": "Causal Anomaly: Document Exported on Server After Transmission Date",
                                "description": (
                                    f"Email ({eml.get('locator', 'Message-ID')}) purports to attach unreleased patent draft at "
                                    f"{format_utc_and_ist(eml_dt)['ist_display']}, but server security log records file export "
                                    f"{mins} minutes later at {format_utc_and_ist(log_dt)['ist_display']}."
                                ),
                                "discrepancy_delta": f"Server export recorded {mins} minutes subsequent to claimed transmission.",
                                "fact_ids": [eml["id"], log["id"]],
                                "benign_explanations": [
                                    "Sender sent an initial draft copy and subsequently re-downloaded an archived revision.",
                                    "Client workstation clock was set forward or unsynchronized relative to server hardware clock.",
                                    "Message was held in outgoing MTA mail delivery queue prior to actual socket transmission."
                                ],
                                "detected_at": datetime.now(timezone.utc).isoformat()
                            })
                            break

        return anomalies

    # --------------------------------------------------------------------------
    # RULE 4: CRYPTOGRAPHIC DUPLICATES WITH RENAMED METADATA
    # --------------------------------------------------------------------------
    @classmethod
    def _detect_cryptographic_duplicates(
        cls,
        evidence_items: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        anomalies = []
        hash_map: Dict[str, Dict[str, Any]] = {}

        for item in evidence_items:
            sha = str(item.get("sha256", "")).lower().strip()
            if not sha or sha == "0" * 64:
                continue

            if sha in hash_map:
                original = hash_map[sha]
                inc_id = f"INC-STR-{uuid.uuid4().hex[:6].upper()}"
                anomalies.append({
                    "id": inc_id,
                    "rule_id": "RULE_DUPLICATE_SHA256_COLLISION",
                    "category": "Structural Integrity",
                    "severity": "MEDIUM",
                    "title": "Identical Content (Bit-Exact SHA-256) under Different File Identities",
                    "description": (
                        f"Exhibit [{item.get('id')}: {item.get('filename')}] shares exact SHA-256 digest ({sha[:16]}...) "
                        f"with previously seized Exhibit [{original.get('id')}: {original.get('filename')}]."
                    ),
                    "discrepancy_delta": "Zero byte difference between two differently named seized files.",
                    "fact_ids": [item.get("id", ""), original.get("id", "")],
                    "benign_explanations": [
                        "Investigator created duplicate forensic working copy during acquisition triage.",
                        "User renamed original document without altering underlying file payload.",
                        "Symlink or hardlink present on original seized file system."
                    ],
                    "detected_at": datetime.now(timezone.utc).isoformat()
                })
            else:
                hash_map[sha] = item

        return anomalies

    # --------------------------------------------------------------------------
    # RULE 5: TIMEZONE SPOOFING & CLOCK INVERSION IN HEADERS
    # --------------------------------------------------------------------------
    @classmethod
    def _detect_timezone_clock_spoofing(
        cls,
        email_facts: List[Dict[str, Any]],
        chat_facts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        anomalies = []
        # Inspect for impossible future timestamps
        now_dt = datetime.now(timezone.utc)
        for f in email_facts + chat_facts:
            dt = parse_iso_datetime(f.get("t_min") or "")
            if dt and dt > now_dt + timedelta(hours=24):
                inc_id = f"INC-CLK-{uuid.uuid4().hex[:6].upper()}"
                anomalies.append({
                    "id": inc_id,
                    "rule_id": "RULE_FUTURE_TIMESTAMP_DETECTED",
                    "category": "Timestamp Inversion",
                    "severity": "HIGH",
                    "title": "Future Dated Event: Device Clock Ahead of Physical Time",
                    "description": f"Fact ({f.get('locator')}) has timestamp in the future: {dt.isoformat()}.",
                    "discrepancy_delta": f"Timestamp is {int((dt - now_dt).total_seconds() / 3600)}h in the future.",
                    "fact_ids": [f.get("id", "")],
                    "benign_explanations": [
                        "Client device CMOS battery depleted, resetting or offsetting system clock.",
                        "Investigator extraction workstation timezone misconfigured during import.",
                        "User manually changed system time for software testing or expired trial license."
                    ],
                    "detected_at": datetime.now(timezone.utc).isoformat()
                })

        return anomalies


# Backward-compatible function alias for existing callers
def detect_inconsistencies(
    facts: List[Dict[str, Any]],
    evidence_items: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Backward-compatible entry point for detect_inconsistencies."""
    return InconsistencyRadarEngine.detect_all_inconsistencies(facts, evidence_items)
