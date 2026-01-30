# src/utils/dates.py

"""
DATE NORMALIZATION UTILITIES
=============================

This module standardizes date formats across the system.

Web sources provide dates in many inconsistent formats.
These functions convert them into a clean ISO format:
    YYYY-MM-DD

This ensures consistency for:
- Metadata storage
- Report citations
- Chronological comparisons
"""

from datetime import datetime
import re


def normalize_date(date_str: str | None) -> str | None:
    """
    Attempts to convert various date formats into ISO format.

    Input:
        Raw date string extracted from web metadata.

    Output:
        Standardized string in "YYYY-MM-DD" format, or None if invalid.
    """

    # If no date provided, return None
    if not date_str:
        return None

    # First try strict ISO parsing
    try:
        return datetime.fromisoformat(date_str).date().isoformat()
    except Exception:
        pass

    # If not ISO, try extracting a date pattern using regex
    # Looks for pattern like: 2024-03-18
    match = re.search(r"\d{4}-\d{2}-\d{2}", date_str)
    if match:
        return match.group(0)

    # If all parsing fails, discard date
    return None


def today_iso() -> str:
    """
    Returns today's date in ISO format (UTC).

    Used to record when a source was retrieved,
    ensuring reproducibility and traceability.
    """
    return datetime.utcnow().date().isoformat()
