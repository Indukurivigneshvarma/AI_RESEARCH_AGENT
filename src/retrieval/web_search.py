# src/retrieval/web_search.py

from src.retrieval.tavily_client import tavily_search


def search_web(
    query: str,
    max_results: int = 3,
):
    """
    WEB SEARCH ABSTRACTION LAYER
    ============================

    This function acts as a thin wrapper over the Tavily search client.
    It exists to keep the pipeline independent from the underlying
    search provider. If the search provider changes in the future,
    only this layer needs modification — not the pipeline logic.

    Parameters
    ----------
    query : str
        The search query generated during the research discovery phase.

    max_results : int
        Number of search results to request from the web search API.

    Returns
    -------
    List of search result metadata dictionaries provided by Tavily.
    """
    
    # Delegates actual search to Tavily client
    return tavily_search(
        query=query,
        max_results=max_results,
    )
