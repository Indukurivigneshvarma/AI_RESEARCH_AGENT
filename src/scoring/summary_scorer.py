from src.scoring.credibility_loader import CredibilityStore
from urllib.parse import urlparse
from datetime import datetime


CRED_STORE = CredibilityStore()

VENUE_SCORES = {
    "journal": 3,
    "repository": 2,
    "book series": 1,
}


def _extract_domain(url: str | None) -> str | None:
    if not url:
        return None
    netloc = urlparse(url).netloc.lower()
    return netloc.replace("www.", "")


def _compute_date_score(date_str: str | None) -> int:
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


def compute_summary_score(summary_record: dict) -> int:
    score = 0

    author = summary_record.get("author")
    if author and author.strip().lower() in CRED_STORE.authors:
        score += 5

    domain = (
        summary_record.get("domain")
        or _extract_domain(summary_record.get("url"))
    )

    if domain and domain in CRED_STORE.sources:
        score += 5
        venue = CRED_STORE.sources[domain]
        score += VENUE_SCORES.get(venue, 0)

    date_published = summary_record.get("date_published")
    score += _compute_date_score(date_published)

    return score
