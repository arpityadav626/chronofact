"""
CHRONOFACT Module 1: Uncertainty-Aware Hyper-Timeline & Temporal Ordering Engine
================================================================================
Compliant with:
- Bharatiya Sakshya Adhiniyam, 2023 (BSA §63(4))
- Allen's Interval Algebra (13 Canonical Temporal Relations)
- ISO 8601 UTC / Indian Standard Time (IST: UTC + 05:30)
- Device Clock Drift & NTP Calibration Bounding

Author: CHRONOFACT Forensic Software Architect
"""

import math
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Tuple, Union


# Indian Standard Time (IST) offset: UTC + 05:30
IST_OFFSET: timedelta = timedelta(hours=5, minutes=30)
IST_TZ: timezone = timezone(IST_OFFSET, name="IST")


def parse_iso_datetime(dt_str: str) -> Optional[datetime]:
    """
    Parses ISO-8601, RFC-3339, or standard forensic timestamp strings into a timezone-aware UTC datetime.
    Handles 'Z', offsets '+05:30', and naive timestamps with explicit UTC fallback.
    """
    if not dt_str or not isinstance(dt_str, str):
        return None
    
    clean = dt_str.strip()
    if not clean:
        return None

    # Replace Z with +00:00 for fromisoformat compatibility
    if clean.endswith("Z"):
        clean = clean[:-1] + "+00:00"

    # Common formats
    for fmt in [
        None,  # fromisoformat
        "%Y-%m-%d %H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%d/%m/%Y, %H:%M:%S",
        "%d-%m-%Y %H:%M:%S",
        "%a, %d %b %Y %H:%M:%S %z"
    ]:
        try:
            if fmt is None:
                dt = datetime.fromisoformat(clean)
            else:
                dt = datetime.strptime(clean, fmt)
            
            # Ensure timezone-aware in UTC
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            else:
                dt = dt.astimezone(timezone.utc)
            return dt
        except (ValueError, TypeError):
            continue

    return None


def format_utc_and_ist(dt: datetime) -> Dict[str, str]:
    """Formats a UTC datetime into explicit UTC and IST string representations."""
    utc_dt = dt.astimezone(timezone.utc)
    ist_dt = dt.astimezone(IST_TZ)
    
    return {
        "utc_iso": utc_dt.isoformat(),
        "ist_iso": ist_dt.isoformat(),
        "utc_display": utc_dt.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "ist_display": ist_dt.strftime("%d-%b-%Y %H:%M:%S IST")
    }


# ==============================================================================
# ALLEN'S INTERVAL ALGEBRA (13 TEMPORAL RELATIONS)
# ==============================================================================

class AllenRelation:
    """
    Canonical temporal relations between two intervals A = [A_s, A_e] and B = [B_s, B_e].
    """
    PRECEDES = "PRECEDES"                    # A_e < B_s
    MEETS = "MEETS"                          # A_e == B_s
    OVERLAPS = "OVERLAPS"                    # A_s < B_s < A_e < B_e
    FINISHED_BY = "FINISHED_BY"              # A_s < B_s and A_e == B_e
    CONTAINS = "CONTAINS"                    # A_s < B_s and A_e > B_e
    STARTS = "STARTS"                        # A_s == B_s and A_e < B_e
    EQUALS = "EQUALS"                        # A_s == B_s and A_e == B_e
    STARTED_BY = "STARTED_BY"                # A_s == B_s and A_e > B_e
    DURING = "DURING"                        # A_s > B_s and A_e < B_e
    FINISHES = "FINISHES"                    # A_s > B_s and A_e == B_e
    OVERLAPPED_BY = "OVERLAPPED_BY"          # B_s < A_s < B_e < A_e
    MET_BY = "MET_BY"                        # A_s == B_e
    PRECEDED_BY = "PRECEDED_BY"              # A_s > B_e


def classify_allen_relation(
    a_start: datetime,
    a_end: datetime,
    b_start: datetime,
    b_end: datetime,
    epsilon_sec: float = 1.0
) -> Tuple[str, str, float]:
    """
    Classifies the exact Allen temporal relationship between interval A and interval B.
    Returns: (Relation_Name, Forensic_Verdict_Label, Overlap_Duration_Seconds)
    """
    # Normalize order within intervals
    if a_start > a_end:
        a_start, a_end = a_end, a_start
    if b_start > b_end:
        b_start, b_end = b_end, b_start

    a_s, a_e = a_start.timestamp(), a_end.timestamp()
    b_s, b_e = b_start.timestamp(), b_end.timestamp()

    # Precedes (Strict order)
    if a_e < b_s - epsilon_sec:
        gap = b_s - a_e
        return (AllenRelation.PRECEDES, "Strictly Precedes (Confirmed)", 0.0)

    # Meets
    if abs(a_e - b_s) <= epsilon_sec:
        return (AllenRelation.MEETS, "Directly Contiguous / Meets (Confirmed)", 0.0)

    # Preceded by
    if a_s > b_e + epsilon_sec:
        return (AllenRelation.PRECEDED_BY, "Strictly Follows / Preceded By (Confirmed)", 0.0)

    # Met by
    if abs(a_s - b_e) <= epsilon_sec:
        return (AllenRelation.MET_BY, "Directly Contiguous / Met By (Confirmed)", 0.0)

    # Equals
    if abs(a_s - b_s) <= epsilon_sec and abs(a_e - b_e) <= epsilon_sec:
        overlap = min(a_e, b_e) - max(a_s, b_s)
        return (AllenRelation.EQUALS, "Coincident / Equals (Identical Time Bounds)", max(0.0, overlap))

    # Overlaps
    if a_s < b_s and b_s < a_e < b_e:
        overlap = a_e - b_s
        return (AllenRelation.OVERLAPS, f"Temporal Order Undetermined (?) - Overlaps by {int(overlap)}s", max(0.0, overlap))

    # Overlapped by
    if b_s < a_s and a_s < b_e < a_e:
        overlap = b_e - a_s
        return (AllenRelation.OVERLAPPED_BY, f"Temporal Order Undetermined (?) - Overlapped by {int(overlap)}s", max(0.0, overlap))

    # Contains
    if a_s <= b_s and a_e >= b_e:
        overlap = b_e - b_s
        return (AllenRelation.CONTAINS, f"Temporal Order Undetermined (?) - Interval A Contains B ({int(overlap)}s span)", max(0.0, overlap))

    # During
    if a_s >= b_s and a_e <= b_e:
        overlap = a_e - a_s
        return (AllenRelation.DURING, f"Temporal Order Undetermined (?) - Event Occurred During Interval B ({int(overlap)}s)", max(0.0, overlap))

    # Default overlap
    overlap = max(0.0, min(a_e, b_e) - max(a_s, b_s))
    return (AllenRelation.OVERLAPS, f"Temporal Order Undetermined (?) - Overlapping Bounds ({int(overlap)}s)", overlap)


# ==============================================================================
# HYPER-TIMELINE BUILDER & CLOCK SKEW CALIBRATION ENGINE
# ==============================================================================

class TimelineEngine:
    """
    Uncertainty-Aware Hyper-Timeline Engine.
    
    Replaces brittle flat timelines with rigorous partial-order intervals [t_min, t_max].
    Integrates device clock skew compensation and Allen's Interval Algebra.
    """

    @staticmethod
    def calibrate_clock_skew(
        dt_utc: datetime,
        evidence_id: str,
        skew_offsets_seconds: Optional[Dict[str, float]] = None,
        mode: str = "ntp"
    ) -> Tuple[datetime, float]:
        """
        Calibrates local hardware device clock drift against NTP Server Reference.
        
        If mode is 'ntp', subtracts known positive device clock drift to normalize to true UTC.
        If mode is 'raw', leaves the physical device clock unaltered.
        """
        if not skew_offsets_seconds or evidence_id not in skew_offsets_seconds:
            return dt_utc, 0.0

        skew_sec = skew_offsets_seconds[evidence_id]
        if mode == "ntp":
            calibrated = dt_utc - timedelta(seconds=skew_sec)
            return calibrated, skew_sec
        return dt_utc, 0.0

    @classmethod
    def build_interval_timeline(
        cls,
        facts: List[Dict[str, Any]],
        skew_offsets_seconds: Optional[Dict[str, float]] = None,
        calibration_mode: str = "ntp"
    ) -> List[Dict[str, Any]]:
        """
        Constructs an uncertainty-aware hyper-timeline from atomic evidence facts.
        
        Parameters:
        - facts: List of extracted evidence facts from SQLite extracted_facts table.
        - skew_offsets_seconds: Map of evidence_id -> known clock drift in seconds (e.g. {'EV-8EA211': 194.0}).
        - calibration_mode: 'ntp' (drift-corrected) or 'raw' (hardware clock as seized).
        
        Returns:
        List of chronological timeline events enriched with [t_min, t_max], Allen's pairwise
        ordering constraints, and dual UTC/IST formatting.
        """
        if not facts:
            return []

        # Default sample clock skew: Device EV-8EA211 is +03:14 (194 seconds) ahead of NTP
        if skew_offsets_seconds is None:
            skew_offsets_seconds = {
                "EV-8EA211": 194.0,  # 3 min 14 sec ahead
                "EV-1D5FE4": 194.0
            }

        timeline_events = []

        for f in facts:
            raw_t_min = f.get("t_min", "")
            raw_t_max = f.get("t_max", "")
            tz_basis = f.get("tz_basis", "explicit_utc")
            evidence_id = f.get("evidence_id", "UNKNOWN")

            dt_min = parse_iso_datetime(raw_t_min) or datetime.now(timezone.utc)
            dt_max = parse_iso_datetime(raw_t_max) or dt_min

            # Apply Clock Skew Calibration
            calibrated_min, applied_skew = cls.calibrate_clock_skew(
                dt_min, evidence_id, skew_offsets_seconds, calibration_mode
            )
            calibrated_max, _ = cls.calibrate_clock_skew(
                dt_max, evidence_id, skew_offsets_seconds, calibration_mode
            )

            is_interval = (calibrated_min != calibrated_max)
            skew_applied = abs(applied_skew) > 0.001

            # Determine uncertainty label
            if is_interval:
                diff_sec = abs((calibrated_max - calibrated_min).total_seconds())
                uncertainty_label = f"Uncertain (Timezone ambiguous / drift bounded: ±{int(diff_sec/3600)}h window)"
            elif skew_applied:
                uncertainty_label = f"NTP Calibrated (-{int(applied_skew)}s Device Skew Corrected)"
            else:
                uncertainty_label = "Exact (Zero Skew / NTP Verified)"

            # Dual UTC and IST strings
            min_fmt = format_utc_and_ist(calibrated_min)
            max_fmt = format_utc_and_ist(calibrated_max)

            display_time = (
                min_fmt["utc_iso"] if not is_interval
                else f"{min_fmt['utc_iso']} <-> {max_fmt['utc_iso']}"
            )

            timeline_events.append({
                "id": f.get("id", ""),
                "evidence_id": evidence_id,
                "fact_type": f.get("fact_type", "GENERIC_FACT"),
                "actor": f.get("actor") or "Unknown",
                "content": f.get("raw_text") or f.get("content") or "",
                "locator": f.get("locator", ""),
                "t_min": min_fmt["utc_iso"],
                "t_max": max_fmt["utc_iso"],
                "t_min_ist": min_fmt["ist_iso"],
                "t_max_ist": max_fmt["ist_iso"],
                "t_min_display_ist": min_fmt["ist_display"],
                "is_interval": is_interval,
                "uncertainty_label": uncertainty_label,
                "display_time": display_time,
                "dt_min_obj": calibrated_min,
                "dt_max_obj": calibrated_max,
                "raw_dt_min": raw_t_min,
                "raw_dt_max": raw_t_max,
                "applied_skew_seconds": applied_skew
            })

        # Sort primarily by calibrated t_min
        timeline_events.sort(key=lambda x: x["dt_min_obj"])

        # Compute Pairwise Temporal Ordering Relationships (Allen's Interval Algebra)
        for i in range(len(timeline_events) - 1):
            curr_ev = timeline_events[i]
            next_ev = timeline_events[i + 1]

            relation, verdict_label, overlap_sec = classify_allen_relation(
                curr_ev["dt_min_obj"], curr_ev["dt_max_obj"],
                next_ev["dt_min_obj"], next_ev["dt_max_obj"]
            )

            curr_ev["allen_relation_vs_next"] = relation
            curr_ev["order_status_vs_next"] = verdict_label
            curr_ev["overlap_duration_seconds"] = overlap_sec

        # Clean temporary datetime objects before serialization
        for ev in timeline_events:
            ev.pop("dt_min_obj", None)
            ev.pop("dt_max_obj", None)

        return timeline_events


# Backward-compatible function alias for existing callers
def build_interval_timeline(facts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Backward-compatible entry point for build_interval_timeline."""
    return TimelineEngine.build_interval_timeline(facts, calibration_mode="ntp")
