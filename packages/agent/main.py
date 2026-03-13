from typing import Dict, Optional

from state import AgentState

from gradient_adk import entrypoint, RequestContext
from langgraph.graph import StateGraph, END
from agents.analyst import analyst
from agents.researcher import researcher
from agents.scraper import scraper

AGENT_GRAPH: Optional[StateGraph] = None


async def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    # Nodes
    graph.add_node("analyst", analyst)
    graph.add_node("researcher", researcher)
    graph.add_node("scraper", scraper)

    # Edges
    graph.set_entry_point("analyst")
    graph.add_edge("analyst", "researcher")
    graph.add_edge("researcher", "scraper")
    graph.add_edge("scraper", END)

    return graph.compile()


@entrypoint
async def main(payload: Dict[str, str], context: RequestContext):
    """Entrypoint"""

    repo_url = payload.get("repo_url")
    if not repo_url:
        return {"error": "repo_url is required"}

    # Build graph once and cache it.
    global AGENT_GRAPH
    if AGENT_GRAPH is None:
        AGENT_GRAPH = await build_graph()

    initial_state: AgentState = {
        "repo_url": repo_url,
        "project_name": repo_url.split("/")[-1],
        "dependencies": [],
        "docs_urls": [],
        "docs_urls_content": [],
        "stored": False,
    }

    # Invoke app
    resp = await AGENT_GRAPH.ainvoke(initial_state, {"recursion_limit": 100})
    return {
        "project_name": resp["project_name"],
        "documentation_urls": resp["docs_urls"],
        "dep_docs": resp["docs_url_content"],
    }
