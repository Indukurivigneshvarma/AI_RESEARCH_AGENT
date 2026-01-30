# src/report/citations.py

from typing import List, Dict 


def build_references(
    summaries: List[Dict],
) -> List[str]:
    """
    REFERENCE LIST BUILDER
    ======================

    Purpose
    -------
    Converts internal summary records into a clean, human-readable
    reference list for the final report.

    This function bridges:
        Internal evidence objects  →  External citation section

    Each summary becomes one reference entry, keyed by its summary ID.

    Expected summary fields:
        id      → Internal summary identifier (e.g., S1, S2)
        author  → Extracted author (may be None)
        domain  → Source domain (e.g., arxiv.org, nature.com)
        url     → Original source URL

    Output format:
        [S1] Author Name. domain.com. https://...

    Notes
    -----
    • This is NOT a formal citation style (APA/MLA/etc.)
      It is an *evidence traceability format*.
    • Designed for:
        - Transparency
        - Auditability
        - Source backtracking
    """

    refs = []

    for s in summaries:
        # Unique summary identifier used throughout the system
        sid = s["id"]

        # Fallbacks ensure report generation never crashes due to missing metadata
        author = s.get("author") or "Unknown Author"
        domain = s.get("domain") or "Unknown Source"
        url = s.get("url") or ""

        # Simple structured reference entry
        refs.append(f"[{sid}] {author}. {domain}. {url}")

    return refs
