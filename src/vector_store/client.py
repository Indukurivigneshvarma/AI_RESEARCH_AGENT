# src/vector_store/client.py

"""
VECTOR STORE CLIENT
====================

Persistent FAISS-based memory for research summaries.
"""

import json
from typing import List, Dict
import numpy as np
import faiss

from src.config import FAISS_INDEX_PATH, FAISS_META_PATH


class VectorStoreClient:
    """
    Persistent FAISS vector store for SUMMARY-LEVEL records.
    """

    def __init__(self, embedding_dim: int = 384):
        """
        Initializes the vector store.

        embedding_dim must match the embedding model used in retrieval.
        """

        self.embedding_dim = embedding_dim
        self.index_path = str(FAISS_INDEX_PATH)
        self.meta_path = str(FAISS_META_PATH)

        # Ensure parent directory exists (vector_data/)
        FAISS_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)

        self._load_or_create()

    # --------------------------------------------------
    # Initialization
    # --------------------------------------------------

    def _load_or_create(self):
        """Loads existing FAISS memory or creates a new index."""

        if FAISS_INDEX_PATH.exists():
            self.index = faiss.read_index(self.index_path)
        else:
            self.index = faiss.IndexFlatIP(self.embedding_dim)

        if FAISS_META_PATH.exists():
            with open(self.meta_path, "r", encoding="utf-8") as f:
                self.metadata: List[Dict] = json.load(f)
        else:
            self.metadata = []

        if self.index.ntotal != len(self.metadata):
            raise RuntimeError("FAISS index and metadata out of sync.")

    # --------------------------------------------------
    # Search
    # --------------------------------------------------

    def search(self, embedding: List[float], top_k: int) -> List[Dict]:
        if self.index.ntotal == 0:
            return []

        query = np.array([embedding], dtype="float32")
        _, idxs = self.index.search(query, top_k)

        results = []
        for i in idxs[0]:
            if i == -1:
                continue
            results.append(self.metadata[i])

        return results

    # --------------------------------------------------
    # Upsert (append-only)
    # --------------------------------------------------

    def upsert(self, records: List[Dict]):
        if not records:
            return

        vectors = np.array(
            [r["embedding"] for r in records],
            dtype="float32",
        )

        self.index.add(vectors)
        self.metadata.extend(records)

        self._persist()

    # --------------------------------------------------
    # Persistence
    # --------------------------------------------------

    def _persist(self):
        faiss.write_index(self.index, self.index_path)

        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
