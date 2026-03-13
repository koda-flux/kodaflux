import hashlib
import json
import os
import re
from pathlib import Path

from firecrawl import FirecrawlApp
from langchain_gradient import ChatGradient
from langchain_core.messages import SystemMessage, HumanMessage

from state import AgentState
from agents.prompts import RESEARCHER_PROMPTS


model = ChatGradient(model=os.getenv("DIGITALOCEAN_INFERENCE_MODEL"))
firecrawl = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

CACHE_DIR = Path(".cache")
CACHE_DIR.mkdir(exist_ok=True)


def cache_key(dep_name: str) -> Path:
    key = hashlib.md5(dep_name.lower().encode()).hexdigest()
    return CACHE_DIR / f"{key}.json"


def read_cache(dep_name: str) -> dict | None:
    path = cache_key(dep_name)
    try:
        if path.exists():
            return json.loads(path.read_text())
    except Exception:
        pass
    return None


def write_cache(dep_name: str, result: dict) -> None:
    try:
        cache_key(dep_name).write_text(json.dumps(result))
    except Exception:
        pass


def firecrawl_search(dep_name: str) -> str:
    """
    Uses Firecrawl's search endpoint to find the dep's docs page.
    Returns the raw search result text to pass to the LLM.
    """
    results = firecrawl.search(
        f"{dep_name} official documentation quickstart getting started",
        limit=5,
    )
    if not results or not results.web:
        return ""

    # Format results as readable text for the LLM to reason over
    lines = []
    for item in results.web:
        title = getattr(item, "title", "")
        url = getattr(item, "url", "")
        description = getattr(item, "description", "")
        lines.append(f"- {title}\n  URL: {url}\n  {description}")

    return "\n\n".join(lines)


async def search_for_dep(dep_name: str) -> dict:
    # Return cached result if available
    cached = read_cache(dep_name)
    if cached is not None:
        print(f"[cache hit] {dep_name}")
        return cached

    # Search via Firecrawl
    search_results = firecrawl_search(dep_name)

    if not search_results:
        result = {"name": dep_name, "url": None}
        write_cache(dep_name, result)
        return result

    # Ask the LLM to pick the best URL from the search results
    messages = [
        SystemMessage(content=RESEARCHER_PROMPTS["system"]),
        HumanMessage(
            content=(
                f"Dependency: {dep_name}\n\n"
                f"Search results:\n{search_results}\n\n"
                f"Based on these results, return the JSON object."
            )
        ),
    ]

    response = await model.ainvoke(messages)
    raw = re.sub(
        r"^```json|^```|```$", "", response.content.strip(), flags=re.MULTILINE
    ).strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = {"name": dep_name, "url": None}

    # Cache the result before returning
    write_cache(dep_name, result)
    return result


async def researcher(state: AgentState) -> AgentState:
    doc_urls: dict[str, str] = {}

    for dep in state.get("dependencies", []):
        result = await search_for_dep(dep)
        if result.get("url"):
            doc_urls[result["name"]] = result["url"]

    return {**state, "docs_urls": doc_urls}
