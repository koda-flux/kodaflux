from tools.site_scraper import scrape_url
from state import AgentState


async def scraper(state: AgentState) -> AgentState:
    doc_urls = state.get("docs_urls", {})
    site_content = []

    for name, url in doc_urls.items():
        markdown = scrape_url(url)
        site_content.append(
            {
                "name": name,
                "url": url,
                "markdown": markdown,
            }
        )

    return {**state, "docs_url_content": site_content}
