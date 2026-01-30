# src/retrieval/cross_encoder.py

from typing import List, Dict
from sentence_transformers import CrossEncoder


class CrossEncoderReranker:
    """
    CROSS-ENCODER RERANKER
    =======================

    This component improves retrieval precision by
    reranking vector-search candidates using a
    cross-encoder model.

    Difference from vector search:
    - Vector search = approximate similarity (fast)
    - Cross-encoder = deep semantic matching (accurate)

    The cross-encoder reads BOTH the query and candidate text
    together and assigns a relevance score.
    """

    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
    ):
        # Load pretrained cross-encoder for passage ranking
        self.model = CrossEncoder(model_name)

    def rerank(
        self,
        query: str,
        candidates: List[Dict],
        top_k: int = 5,
    ) -> List[Dict]:
        """
        Reranks candidate queries/summaries.

        Parameters
        ----------
        query : str
            The user subquery.

        candidates : List[Dict]
            Candidate items from vector search.
            Each must contain "query_text".

        top_k : int
            Number of top results to return.

        Returns
        -------
        Top-k candidates sorted by semantic relevance.
        """

        # No candidates → nothing to rerank
        if not candidates:
            return []

        # Create (query, candidate_text) pairs
        # Required input format for cross-encoder
        pairs = [
            (query, c["query_text"])
            for c in candidates
        ]

        # Predict semantic relevance scores
        scores = self.model.predict(pairs)

        # Attach scores to candidate records
        for c, score in zip(candidates, scores):
            c["score"] = float(score)

        # Sort by score (descending = most relevant first)
        ranked = sorted(
            candidates,
            key=lambda x: x["score"],
            reverse=True,
        )

        # Return only top-k results
        return ranked[:top_k]
