# src/retrieval/tavily_client.py

import os
from tavily import TavilyClient
from urllib.parse import urlparse


# --------------------------------------------------
# TAVILY CLIENT INITIALIZATION
# --------------------------------------------------
# Uses API key from environment variables.
# This client performs both search and content extraction.
_tavily = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)


# --------------------------------------------------
# SEARCH FUNCTION
# --------------------------------------------------
def tavily_search(
    query: str,
    max_results: int = 3,
):
    """
    Performs web search using Tavily.

    Parameters
    ----------
    query : str
        Research subquery.

    max_results : int
        Number of URLs to return.

    Returns
    -------
    List of search result objects (metadata only).
    Content is NOT retrieved at this stage.
    """
    response = _tavily.search(
        query=query,
        search_depth="advanced",     # deeper search strategy
        max_results=max_results,
        include_raw_content=False,   # content fetched later
        include_answer=False,        # we want sources, not Tavily answers
    )
    return response.get("results", [])


# --------------------------------------------------
# CONTENT EXTRACTION
# --------------------------------------------------
def tavily_extract(url: str):
    """
    Fetches and extracts main textual content from a webpage.

    Used after selecting URLs during web ingestion.

    Returns:
        {
            "url": original URL,
            "domain": extracted domain,
            "raw_text": article/page content,
            "published_date": metadata date (if available)
        }
    """

    response = _tavily.extract(
        urls=[url],
        include_raw_content=True,  # needed for LLM summarization
    )

    data = response.get("results", [])
    if not data:
        return None

    item = data[0]

    # Normalize domain (remove www)
    domain = urlparse(url).netloc.replace("www.", "")

    return {
        "url": url,
        "domain": domain,
        # Prefer raw content if available, fallback to extracted text
        "raw_text": item.get("raw_content") or item.get("content"),
        "published_date": item.get("published_date"),
    }
