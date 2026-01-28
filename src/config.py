# src/config.py

from pathlib import Path

# --------------------------------------------------
# Project Root (auto-resolves no matter where run from)
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------
# Data Paths
# --------------------------------------------------
DATA_DIR = BASE_DIR / "data"
CREDIBILITY_DIR = DATA_DIR / "credibility"

AUTHORS_PATH = CREDIBILITY_DIR / "authors.xlsx"
SOURCES_PATH = CREDIBILITY_DIR / "sources.xlsx"

# --------------------------------------------------
# Vector Store Paths (runtime-generated, NOT committed)
# --------------------------------------------------
VECTOR_DATA_DIR = BASE_DIR / "vector_data"
FAISS_INDEX_PATH = VECTOR_DATA_DIR / "index.faiss"
FAISS_META_PATH = VECTOR_DATA_DIR / "metadata.json"

# --------------------------------------------------
# Vector search
# --------------------------------------------------
VECTOR_TOP_K = 10
CROSS_TOP_K = 5

# --------------------------------------------------
# Web ingestion limits
# --------------------------------------------------
MIN_RAW_CHARS = 1200
MAX_RAW_CHARS = 8000

MAX_SUMMARY_TOKENS = 1000

# --------------------------------------------------
# Research modes
# --------------------------------------------------
MODES = {
    "quick": {
        "iterations": 1,              # only initial discovery
        "queries_per_iteration": 2,
    },
    "standard": {
        "iterations": 2,              # +1 coverage refinement
        "queries_per_iteration": 2,
    },
    "deep": {
        "iterations": 3,              # +2 coverage refinements
        "queries_per_iteration": 2,
    },
}
