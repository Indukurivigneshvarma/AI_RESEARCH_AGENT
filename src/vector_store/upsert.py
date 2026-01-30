# src/vector_store/upsert.py

"""
VECTOR STORE UPSERT LOGIC
==========================

This module ensures that summaries are inserted into the vector
memory **without duplicates**.

Its main purpose is to prevent the system from storing the same
source multiple times across research sessions.
"""

from typing import List, Dict, Tuple

# Client that manages FAISS index + metadata storage
from src.vector_store.client import VectorStoreClient


# --------------------------------------------------
# FINGERPRINTING STRATEGY
# --------------------------------------------------

def _fingerprint(r: Dict) -> Tuple:
    """
    Creates a unique identity key for each summary record.

    Currently, the system uses the URL as the uniqueness key.
    This means:
        Same URL → Treated as the same summary
        Different URL → Treated as a new source

    This prevents storing duplicate evidence from the same source.
    """
    return (
        r.get("url"),
    )


# --------------------------------------------------
# DEDUPLICATED UPSERT FUNCTION
# --------------------------------------------------

def upsert_summaries(
    client: VectorStoreClient,
    records: List[Dict],
):
    """
    Inserts summaries into persistent memory **only if they are new**.

    This function acts as a filter before adding data into FAISS.

    Steps:
        1. Collect fingerprints of existing records
        2. Compare incoming records
        3. Insert only unseen summaries
    """

    # Build a set of fingerprints for all already-stored summaries
    existing = {
        _fingerprint(r)
        for r in client.metadata
    }

    new_records = []

    # Check each incoming record
    for r in records:
        fp = _fingerprint(r)

        # Skip if already in memory
        if fp in existing:
            continue

        # Otherwise mark as new
        new_records.append(r)
        existing.add(fp)

    # Insert only new, deduplicated records
    if new_records:
        client.upsert(new_records)
