import os
import hashlib
import json

from pathlib import Path

from agents.prompts import FORMATTER_PROMPTS
from state import AgentState
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_gradient import ChatGradient


model = ChatGradient(model=os.getenv("DIGITALOCEAN_INFERENCE_MODEL"))

CACHE_DIR = Path(os.path.join(".cache", "formatter"))
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def cache_key(url: str) -> Path:
    key = hashlib.md5(url.encode()).hexdigest()
    return CACHE_DIR / f"{key}.json"


def read_cache(url: str) -> str | None:
    path = cache_key(url)
    try:
        if path.exists():
            return json.loads(path.read_text())
    except Exception:
        pass
    return None


def write_cache(url: str, markdown: str) -> None:
    try:
        cache_key(url).write_text(json.dumps({"url": url, "markdown": markdown}))
    except Exception:
        pass


async def formatter(state: AgentState) -> AgentState:
    docs = state.get("docs_url_content", [])
    formatted_docs = []

    for dep in docs:
        name = dep["name"]
        url = dep.get("url", "")
        raw_markdown = dep.get("markdown")

        # Return cached result if available
        cached = read_cache(url)
        if cached is not None:
            print(f"[cache hit] {url}")
            formatted_docs.append({**dep, "markdown": cached["markdown"]})
            continue

        # Write minimal stub if no content was scraped
        if not raw_markdown:
            stub = (
                f"# {name}\n\n"
                f"> No documentation could be retrieved for this package.\n\n"
                f"## Further Reading\n\n"
                f"- [Search for {name}](https://www.google.com/search?q={name}+documentation)\n"
            )
            formatted_docs.append({**dep, "markdown": stub})
            write_cache(url, stub)
            continue

        resp = await model.ainvoke(
            [
                SystemMessage(content=FORMATTER_PROMPTS["system"]),
                HumanMessage(
                    content=FORMATTER_PROMPTS["user"].format(name, url, raw_markdown)
                ),
            ]
        )

        formatted_docs.append({**dep, "markdown": resp.content.strip()})
        write_cache(url, resp.content.strip())
    return {**state, "docs_url_content": formatted_docs}
