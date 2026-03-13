import hashlib
import json
import os
from pathlib import Path

from firecrawl import FirecrawlApp
from langchain_core.tools import tool
import httpx


firecrawl = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

CACHE_DIR = Path(os.path.join(".cache", "scraper"))
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


def is_reachable(url: str) -> bool:
    """
    Returns True only if the URL responds with a 2xx status code.
    Catches connection errors, timeouts, and 4xx/5xx responses.
    """
    try:
        response = httpx.head(
            url,
            follow_redirects=True,
            timeout=5,
            headers={"User-Agent": "Mozilla/5.0 (compatible; Kodaflux/1.0)"},
        )
        if response.status_code < 400:
            with httpx.stream("GET", url, follow_redirects=True, timeout=5) as response:
                return response.status_code < 400
    except Exception:
        return False


@tool
def scrape_url(url: str) -> str | None:
    """
    Scrapes the page found at the URL

    Args:
        url (str): URL to scrape

    Returns:
        Markdown representation of the page at the URL or None of scraping fails
    """
    # Return cached result if available
    cached = read_cache(url)
    if cached is not None:
        print(f"[cache hit] {url}")
        return cached

    # Validate the URL before spending a Firecrawl credit on it
    if not is_reachable(url):
        print(f"[skipped] {url} — not reachable")
        return None

    # Scrape via Firecrawl
    try:
        result = firecrawl.scrape(url, formats=["markdown"])
        markdown = result.markdown
        if markdown:
            write_cache(url, markdown)
        return markdown
    except Exception:
        return None
