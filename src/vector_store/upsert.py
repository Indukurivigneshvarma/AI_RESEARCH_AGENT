# src/vector_store/upsert.py

"""
VECTOR STORE UPSERT LOGIC
==========================
Deduplicated insertion of summaries into persistent vector memory.
"""

from typing import List, Dict, Tuple
from src.vector_store.client import VectorStoreClient


# --------------------------------------------------
# Fingerprinting Strategy
# --------------------------------------------------

def _fingerprint(r: Dict) -> Tuple:
    """Unique identity for a summary (currently URL-based)."""
    return (
        r.get("url"),
    )


# --------------------------------------------------
# Deduplicated Upsert
# --------------------------------------------------

def upsert_summaries(
    client: VectorStoreClient,
    records: List[Dict],
):
    """
    Inserts summaries only if the URL is not already stored.
    """

    existing = {
        _fingerprint(r)
        for r in client.metadata
    }

    new_records = []

    for r in records:
        fp = _fingerprint(r)

        if fp in existing:
            continue

        new_records.append(r)
        existing.add(fp)

    if new_records:
        client.upsert(new_records)
