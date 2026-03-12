from gradient_adk import entrypoint
from typing import Dict
from gradient_adk import RequestContext
from tools.repo_reader import fetch_dependencies
from agents.researcher import find_doc_urls
import os


@entrypoint
async def main(payload: Dict[str, str], context: RequestContext):
    deps = fetch_dependencies(payload["repo_url"], os.getenv("GITHUB_TOKEN"))
    doc_urls = find_doc_urls(deps)
    return {
        "deps": doc_urls,
    }
