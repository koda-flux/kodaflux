from gradient_adk import entrypoint
from typing import Dict
from gradient_adk import RequestContext
import os
from tools.repo_reader import fetch_dependencies
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun


search = DuckDuckGoSearchRun()


@tool
def web_search(query: str) -> str:
    """Perform a web search using DuckDuckGo."""
    results = search.run(query)
    return results


@entrypoint
async def main(payload: Dict[str, str], context: RequestContext):
    deps = fetch_dependencies(payload["repo_url"], os.getenv("GITHUB_TOKEN"))

    return {"deps": deps}
