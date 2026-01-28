import pandas as pd
from src.config import AUTHORS_PATH, SOURCES_PATH


class CredibilityStore:
    def __init__(self):
        self.authors = set()
        self.sources = {}

        self._load_authors(AUTHORS_PATH)
        self._load_sources(SOURCES_PATH)

    def _load_authors(self, path):
        df = pd.read_excel(path)

        self.authors = {
            str(author).strip().lower()
            for author in df["author"].dropna().tolist()
        }

    def _load_sources(self, path):
        df = pd.read_excel(path)

        for _, row in df.iterrows():
            domain = str(row["domain"]).strip().lower()
            venue_type = str(row["venue_type"]).strip().lower()

            if domain:
                self.sources[domain] = venue_type


CRED_STORE = CredibilityStore()
