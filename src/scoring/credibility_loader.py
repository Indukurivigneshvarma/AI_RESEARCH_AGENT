import pandas as pd

# Paths to Excel files that define credibility knowledge
from src.config import AUTHORS_PATH, SOURCES_PATH


class CredibilityStore:
    """
    CREDIBILITY DATA STORE
    =======================

    This class loads external knowledge used for credibility scoring.

    It maintains two key datasets:

    1. Author whitelist:
       A list of recognized or trusted authors.

    2. Source classification:
       Maps website domains to venue types
       (e.g., journal, news, blog, etc.).

    These are later used to assign credibility scores
    to collected research summaries.
    """

    def __init__(self):
        # Set of trusted author names (lowercased for matching)
        self.authors = set()

        # Mapping of domain → venue type
        # Example: "nature.com" → "journal"
        self.sources = {}

        # Load both datasets at startup
        self._load_authors(AUTHORS_PATH)
        self._load_sources(SOURCES_PATH)

    # --------------------------------------------------
    # LOAD AUTHOR DATA
    # --------------------------------------------------
    def _load_authors(self, path):
        """
        Reads Excel file containing trusted authors.

        The file must contain a column named "author".
        All names are normalized to lowercase for comparison.
        """
        df = pd.read_excel(path)

        self.authors = {
            str(author).strip().lower()
            for author in df["author"].dropna().tolist()
        }

    # --------------------------------------------------
    # LOAD SOURCE DOMAIN DATA
    # --------------------------------------------------
    def _load_sources(self, path):
        """
        Reads Excel file mapping domains to venue types.

        Required columns:
            - domain (e.g., "bbc.com")
            - venue_type (e.g., "news", "journal")

        This helps estimate reliability of different source types.
        """
        df = pd.read_excel(path)

        for _, row in df.iterrows():
            domain = str(row["domain"]).strip().lower()
            venue_type = str(row["venue_type"]).strip().lower()

            if domain:
                self.sources[domain] = venue_type


# Global singleton used across the system
# Loaded once to avoid repeated file reads
CRED_STORE = CredibilityStore()
