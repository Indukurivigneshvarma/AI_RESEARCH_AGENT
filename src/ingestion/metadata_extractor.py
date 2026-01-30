# src/ingestion/metadata_extractor.py

from newspaper import Article
from typing import Dict, Optional


def extract_metadata(url: str) -> Dict[str, Optional[str]]:
    """
    METADATA EXTRACTION MODULE
    ==========================

    Extracts basic bibliographic metadata from a webpage.

    This information is later used for:
        • Credibility scoring (author reputation)
        • Recency scoring (publication date)
        • Evidence traceability

    The system does NOT rely on metadata being perfect — it is
    treated as a soft signal, not a strict requirement.

    Parameters
    ----------
    url : str
        Source URL from which content was retrieved.

    Returns
    -------
    Dict with:
        "author"         → author name(s) if detected
        "date_published" → ISO date string if detected
    """

    try:
        # Newspaper3k attempts to download and parse article structure
        article = Article(url)
        article.download()
        article.parse()
    except Exception:
        # Fail-safe: if parsing fails, return empty metadata
        return {
            "author": None,
            "date_published": None,
        }

    # Combine multiple authors into a single string
    author = None
    if article.authors:
        author = ", ".join(article.authors)

    # Normalize publication date
    date_published = None
    if article.publish_date:
        date_published = article.publish_date.date().isoformat()

    return {
        "author": author,
        "date_published": date_published,
    }
