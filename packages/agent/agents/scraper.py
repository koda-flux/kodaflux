import os
import hashlib
import json

from pathlib import Path

from agents.prompts import CLEANER_PROMPTS
from tools.site_scraper import scrape_url
from state import AgentState

from langchain_gradient import ChatGradient
from langchain_core.messages import SystemMessage, HumanMessage


model = ChatGradient(model=os.getenv("DIGITALOCEAN_INFERENCE_MODEL"))

CACHE_DIR = Path(os.path.join(".cache", "cleaner"))
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def cache_key(url: str) -> Path:
    key = hashlib.md5(url.encode()).hexdigest()
    return CACHE_DIR / f"{key}.json"


def read_cache(url: str) -> str | None:
    path = cache_key(url)
    try:
        if path.exists():
            return json.loads(path.read_text())["markdown"]
    except Exception:
        pass
    return None


def write_cache(url: str, markdown: str) -> None:
    try:
        cache_key(url).write_text(json.dumps({"url": url, "markdown": markdown}))
    except Exception:
        pass


async def clean(url: str, markdown: str) -> str:
    """Pass raw scraped markdown through the LLM to strip page chrome."""

    # Read cache before spending on LLM call
    cached = read_cache(url)
    if cached is not None:
        print(f"[cache hit] {url}")
        return cached

    messages = [
        SystemMessage(content=CLEANER_PROMPTS["system"]),
        HumanMessage(content=CLEANER_PROMPTS["user"].format(url, markdown)),
    ]
    response = await model.ainvoke(messages)
    write_cache(url, response.content.strip())
    return response.content.strip()


async def scraper(state: AgentState) -> AgentState:
    doc_urls = state.get("docs_urls", {})
    site_content = []

    for name, url in doc_urls.items():
        raw_markdown = scrape_url(url)
        cleaned_markdown = await clean(url, raw_markdown)
        site_content.append(
            {
                "name": name,
                "url": url,
                "markdown": cleaned_markdown,
            }
        )

    return {**state, "docs_url_content": site_content}
