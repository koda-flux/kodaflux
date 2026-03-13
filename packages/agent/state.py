from typing import List, Dict, TypedDict


class AgentState(TypedDict):
    """The shared state of the graph."""

    repo_url: str
    project_name: str
    dependencies: List[str]
    docs_urls: Dict[str, str]
    docs_url_content: List[Dict[str, str]]
    stored: bool
