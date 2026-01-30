# src/retrieval/vector_search.py

from typing import List, Dict


class VectorSearcher:
    """
    VECTOR SEARCH WRAPPER
    ======================

    This class provides a clean interface for querying the
    persistent FAISS vector store.

    It converts raw vector-store results into the standardized
    structure expected by the research pipeline.
    """

    def __init__(self, vector_client):
        # VectorStoreClient instance (FAISS backend)
        self.client = vector_client

    def search(
        self,
        query_embedding,
        top_k: int,
    ) -> List[Dict]:
        """
        Performs similarity search over stored summaries.

        Parameters
        ----------
        query_embedding : List[float]
            Embedding vector of the current query.

        top_k : int
            Number of nearest summaries to retrieve.

        Returns
        -------
        List of standardized summary records.
        """

        # Query FAISS index via VectorStoreClient
        results = self.client.search(
            embedding=query_embedding,
            top_k=top_k,
        )

        # Normalize records into pipeline-compatible format
        hits = []
        for r in results:
            hits.append({
                "query_text": r["query_text"],      # original query that produced this summary
                "summary": r["summary"],            # stored summary text
                "embedding": r["embedding"],        # stored embedding vector
                "url": r.get("url"),                # source URL
                "domain": r.get("domain"),          # source domain
                "author": r.get("author"),          # extracted author metadata
                "venue_type": r.get("venue_type"),  # type of publication venue
                "date_published": r.get("date_published"),
                "date_retrieved": r.get("date_retrieved"),
            })

        return hits
