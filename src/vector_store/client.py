# src/vector_store/client.py

"""
VECTOR STORE CLIENT
====================

This module implements the system's persistent memory layer.

It stores research summaries as semantic vectors using FAISS,
allowing future research queries to reuse past knowledge instead
of repeating web searches.
"""

import json
from typing import List, Dict
import numpy as np
import faiss

# File paths for storing FAISS index and metadata JSON
from src.config import FAISS_INDEX_PATH, FAISS_META_PATH


class VectorStoreClient:
    """
    Persistent FAISS vector store for SUMMARY-LEVEL records.

    Each stored record represents a summarized research source,
    along with its embedding and metadata (URL, author, etc.).
    """

    def __init__(self, embedding_dim: int = 384):
        """
        Initializes the vector store.

        embedding_dim:
            Must match the embedding model used elsewhere in the system.
            If mismatched, search results would become invalid.
        """

        # Dimension of vectors used in FAISS (MiniLM = 384)
        self.embedding_dim = embedding_dim

        # File paths for index and metadata storage
        self.index_path = str(FAISS_INDEX_PATH)
        self.meta_path = str(FAISS_META_PATH)

        # Ensure storage directory exists (vector_data/)
        FAISS_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)

        # Load existing memory or create a new one
        self._load_or_create()

    # --------------------------------------------------
    # Initialization
    # --------------------------------------------------

    def _load_or_create(self):
        """
        Loads an existing FAISS index and metadata if available.
        Otherwise, creates a new empty index.
        """

        # Load FAISS index (vector memory)
        if FAISS_INDEX_PATH.exists():
            self.index = faiss.read_index(self.index_path)
        else:
            # Inner product index (used for cosine similarity search)
            self.index = faiss.IndexFlatIP(self.embedding_dim)

        # Load metadata (list of summary records)
        if FAISS_META_PATH.exists():
            with open(self.meta_path, "r", encoding="utf-8") as f:
                self.metadata: List[Dict] = json.load(f)
        else:
            self.metadata = []

        # Safety check: index vectors must match metadata entries
        if self.index.ntotal != len(self.metadata):
            raise RuntimeError("FAISS index and metadata out of sync.")

    # --------------------------------------------------
    # Search
    # --------------------------------------------------

    def search(self, embedding: List[float], top_k: int) -> List[Dict]:
        """
        Searches vector memory for semantically similar summaries.

        embedding:
            Vector representation of the current query.

        top_k:
            Number of most similar stored summaries to retrieve.
        """

        # If memory is empty, nothing to retrieve
        if self.index.ntotal == 0:
            return []

        # Convert query to NumPy array for FAISS
        query = np.array([embedding], dtype="float32")

        # Perform similarity search
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
        """
        Adds new summary records to memory.

        Each record must contain:
            - embedding (vector)
            - metadata fields (URL, summary text, etc.)
        """

        if not records:
            return

        # Extract embeddings from records
        vectors = np.array(
            [r["embedding"] for r in records],
            dtype="float32",
        )

        # Add vectors to FAISS index
        self.index.add(vectors)

        # Add corresponding metadata entries
        self.metadata.extend(records)

        # Save changes to disk
        self._persist()

    # --------------------------------------------------
    # Persistence
    # --------------------------------------------------

    def _persist(self):
        """
        Writes FAISS index and metadata to disk so memory persists
        across application restarts.
        """

        # Save vector index
        faiss.write_index(self.index, self.index_path)

        # Save metadata JSON
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)

