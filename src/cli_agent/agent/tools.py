from typing import Any, Literal, List, Callable

from tavily import TavilyClient

tavily_client = TavilyClient()


# Search tool to use to do research
def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a web search"""
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )


TOOLS: List[Callable[..., Any]] = [internet_search]