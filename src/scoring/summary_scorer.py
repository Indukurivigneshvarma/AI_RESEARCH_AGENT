from src.scoring.credibility_loader import CredibilityStore
from urllib.parse import urlparse
from datetime import datetime


# Load global credibility knowledge (authors + source types)
CRED_STORE = CredibilityStore()

# Extra weighting based on publication venue type
# Higher = more authoritative
VENUE_SCORES = {
    "journal": 3,
    "repository": 2,
    "book series": 1,
}


# --------------------------------------------------
# DOMAIN EXTRACTION
# --------------------------------------------------
def _extract_domain(url: str | None) -> str | None:
    """
    Extracts domain from URL.

    Example:
        https://www.nature.com/article → nature.com

    Used when metadata domain is missing.
    """
    if not url:
        return None
    netloc = urlparse(url).netloc.lower()
    return netloc.replace("www.", "")


# --------------------------------------------------
# DATE RECENCY SCORING
# --------------------------------------------------
def _compute_date_score(date_str: str | None) -> int:
    """
    Assigns a recency score.

    Recent sources are weighted higher since they reflect
    up-to-date research.

    < 2 years old → score 2
    Older → score 1
    Unknown date → score 0
    """
    if not date_str:
        return 0

    try:
        pub_date = datetime.fromisoformat(date_str)
        now = datetime.utcnow()
        age_days = (now - pub_date).days

        if age_days < 365 * 2:
            return 2
        return 1
    except Exception:
        return 0


# --------------------------------------------------
# MAIN CREDIBILITY SCORING FUNCTION
# --------------------------------------------------
def compute_summary_score(summary_record: dict) -> int:
    """
    Computes base credibility score for a summary.

    Factors considered:
    1. Author credibility
    2. Source domain reputation
    3. Venue type (journal > repository > book series)
    4. Publication recency

    This score is later combined with agreement score
    to determine overall evidence strength.
    """

    score = 0

    # ---------------- AUTHOR CHECK ----------------
    author = summary_record.get("author")
    if author and author.strip().lower() in CRED_STORE.authors:
        # Trusted author → high weight
        score += 5

    # ---------------- DOMAIN CHECK ----------------
    domain = (
        summary_record.get("domain")
        or _extract_domain(summary_record.get("url"))
    )

    if domain and domain in CRED_STORE.sources:
        # Trusted source → base credibility
        score += 5

        # Add venue-specific weight
        venue = CRED_STORE.sources[domain]
        score += VENUE_SCORES.get(venue, 0)

    # ---------------- DATE RECENCY ----------------
    date_published = summary_record.get("date_published")
    score += _compute_date_score(date_published)

    return score
