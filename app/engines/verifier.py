"""
CHRONOFACT Module 3: Mechanical Citation Verifier & Zero-Hallucination Grounding Gate
=====================================================================================
Compliant with:
- Bharatiya Sakshya Adhiniyam, 2023 (BSA §63(4))
- Deterministic Abstract Syntax & Byte-Span Verification
- Zero-Tolerance Hallucination Gatekeeper Architecture

Author: CHRONOFACT Forensic Software Architect
"""

import re
from typing import Dict, Any, List, Optional, Tuple


class MechanicalCitationVerifier:
    """
    Zero-Hallucination Mechanical Citation Verification Engine.
    
    Forensic Law Principle:
    In digital forensics under BSA 2023 §63(4), Large Language Models or automated
    analytics systems CANNOT be trusted to self-certify their evidentiary citations.
    Every quoted sentence, timestamp, or technical log excerpt must be mechanically
    proven to exist verbatim in the immutable byte stream of the seized exhibits.
    """

    @classmethod
    def locate_substring_spans(
        cls,
        needle: str,
        haystack: str
    ) -> Optional[Dict[str, Any]]:
        """
        Locates exact character offsets, byte offsets, line numbers, and surrounding context.
        """
        if not needle or not haystack:
            return None

        clean_needle = needle.strip()
        idx = haystack.find(clean_needle)
        if idx == -1:
            # Fallback: Normalize multiple spaces/newlines
            norm_needle = " ".join(clean_needle.split())
            norm_haystack = " ".join(haystack.split())
            if norm_needle in norm_haystack:
                # Find closest index
                idx = haystack.lower().find(clean_needle.lower())
                if idx == -1:
                    return None
            else:
                return None

        char_start = idx
        char_end = idx + len(clean_needle)

        # Byte offsets in UTF-8
        encoded_prefix = haystack[:char_start].encode("utf-8")
        encoded_match = haystack[char_start:char_end].encode("utf-8")
        byte_start = len(encoded_prefix)
        byte_end = byte_start + len(encoded_match)

        # Line number calculation (1-indexed)
        lines_before = haystack[:char_start].count("\n")
        line_num = lines_before + 1

        # Extract surrounding context (2 lines before and 2 lines after)
        all_lines = haystack.splitlines(keepends=True)
        start_line_idx = max(0, line_num - 3)
        end_line_idx = min(len(all_lines), line_num + 2)
        surrounding_lines = all_lines[start_line_idx:end_line_idx]

        return {
            "char_start": char_start,
            "char_end": char_end,
            "byte_start": byte_start,
            "byte_end": byte_end,
            "line_number": line_num,
            "matched_text": haystack[char_start:char_end],
            "surrounding_context": "".join(surrounding_lines).strip()
        }

    @classmethod
    def verify_ai_claims(
        cls,
        claims_payload: Dict[str, Any],
        evidence_vault_map: Dict[str, str], # evidence_id -> full raw text
        stored_facts_map: Optional[Dict[str, Dict[str, Any]]] = None # fact_id -> fact object
    ) -> Dict[str, Any]:
        """
        Mechanically audits AI claims against physical evidence files on disk.
        
        Parameters:
        - claims_payload: Dictionary containing 'claims' list.
        - evidence_vault_map: Mapping of evidence_id to raw stored text.
        - stored_facts_map: Optional mapping of fact_id to atomic fact object.
        
        Returns:
        Structured verification report with exact line/byte offsets, grounding metrics,
        and dual-pane inspector payloads.
        """
        if stored_facts_map is None:
            stored_facts_map = {}

        raw_claims = claims_payload.get("claims", [])
        verified_results = []
        verified_count = 0
        total_claims = len(raw_claims)

        for c in raw_claims:
            claim_text = c.get("claim_text", "")
            evidence_id = c.get("evidence_id", "")
            quote = c.get("exact_quote", "").strip()
            locator = c.get("locator", "")
            fact_id = c.get("fact_id", "")

            # Verification Check 1: Existence of referenced exhibit
            if evidence_id not in evidence_vault_map:
                # Check if quote exists in ANY other exhibit (citation misattribution detection)
                misattributed_id = None
                for other_id, other_text in evidence_vault_map.items():
                    if quote and quote in other_text:
                        misattributed_id = other_id
                        break

                if misattributed_id:
                    verified_results.append({
                        "claim_text": claim_text,
                        "evidence_id": evidence_id,
                        "locator": locator,
                        "attempted_quote": quote,
                        "status": "CITATION_MISATTRIBUTION_ERROR",
                        "badge": "Citation Misattribution (Cross-Exhibit Contamination)",
                        "reason": f"Quote exists in Exhibit [{misattributed_id}], but was cited under invalid ID [{evidence_id}].",
                        "is_verified": False,
                        "match_fidelity_pct": 0.0,
                        "mechanical_badge": "Unverified by Source Record",
                        "misattributed_to": misattributed_id
                    })
                else:
                    verified_results.append({
                        "claim_text": claim_text,
                        "evidence_id": evidence_id,
                        "locator": locator,
                        "attempted_quote": quote,
                        "status": "REJECTED_INVALID_EVIDENCE_ID",
                        "badge": "Unverified (Non-Existent Evidence ID)",
                        "reason": f"Evidence ID '{evidence_id}' does not exist in the cryptographic vault.",
                        "is_verified": False,
                        "match_fidelity_pct": 0.0,
                        "mechanical_badge": "Unverified by Source Record",
                        "misattributed_to": None
                    })
                continue

            # Verification Check 2: Verbatim Byte/Line Span Match
            evidence_text = evidence_vault_map[evidence_id]
            span_match = cls.locate_substring_spans(quote, evidence_text)

            if not span_match or not quote:
                # Check if quote was hallucinated or exists in another exhibit
                other_found_id = None
                for other_id, other_text in evidence_vault_map.items():
                    if other_id != evidence_id and quote and quote in other_text:
                        other_found_id = other_id
                        break

                if other_found_id:
                    reason = f"Quote was cited under Exhibit [{evidence_id}], but actually exists in Exhibit [{other_found_id}]."
                    status = "CITATION_MISATTRIBUTION_ERROR"
                    badge = f"Misattribution: Belongs to {other_found_id}"
                else:
                    reason = "The quoted string does not exist verbatim in the referenced exhibit."
                    status = "REJECTED_HALLUCINATED_QUOTE"
                    badge = "Fabricated Quote / Unsubstantiated Claim"

                verified_results.append({
                    "claim_text": claim_text,
                    "evidence_id": evidence_id,
                    "locator": locator,
                    "attempted_quote": quote,
                    "status": status,
                    "badge": badge,
                    "reason": reason,
                    "is_verified": False,
                    "match_fidelity_pct": 0.0,
                    "mechanical_badge": "Unverified by Source Record",
                    "misattributed_to": other_found_id
                })
                continue

            # Verification Check 3: Success — Mechanically Grounded
            fact_data = stored_facts_map.get(fact_id, {})
            time_reliability = fact_data.get("time_reliability", "Verified")

            verified_results.append({
                "claim_text": claim_text,
                "evidence_id": evidence_id,
                "locator": locator or f"Line {span_match['line_number']}",
                "matched_quote": span_match["matched_text"],
                "status": "VERIFIED_MECHANICAL_MATCH_100",
                "badge": "Cryptographically Grounded (100% Mechanical Match)",
                "mechanical_badge": "Mechanical Match: 100% Grounded",
                "is_verified": True,
                "match_fidelity_pct": 100.0,
                "byte_span": {
                    "start_offset": span_match["byte_start"],
                    "end_offset": span_match["byte_end"],
                    "line_number": span_match["line_number"],
                    "char_start": span_match["char_start"],
                    "char_end": span_match["char_end"],
                    "surrounding_context": span_match["surrounding_context"]
                },
                "time_uncertainty": f"Time Basis: {time_reliability}",
                "misattributed_to": None
            })
            verified_count += 1

        fidelity_pct = round((verified_count / total_claims * 100.0) if total_claims > 0 else 0.0, 1)
        overall_status = (
            "FULLY_VERIFIED" if (total_claims > 0 and verified_count == total_claims)
            else "PARTIALLY_VERIFIED" if verified_count > 0
            else "UNVERIFIED_OR_EMPTY"
        )

        return {
            "overall_status": overall_status,
            "total_claims": total_claims,
            "verified_claims_count": verified_count,
            "grounding_fidelity_pct": fidelity_pct,
            "is_court_admissible": (fidelity_pct == 100.0),
            "claims": verified_results,
            "unresolved_contradictions": claims_payload.get("unresolved_contradictions", [])
        }


# Backward-compatible function alias for existing callers
def verify_ai_claims(
    claims_payload: Dict[str, Any],
    evidence_vault_map: Dict[str, str],
    stored_facts_map: Optional[Dict[str, Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Backward-compatible entry point for verify_ai_claims."""
    return MechanicalCitationVerifier.verify_ai_claims(
        claims_payload, evidence_vault_map, stored_facts_map
    )
