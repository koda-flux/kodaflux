from gradient_adk import entrypoint
from typing import Dict
from gradient_adk import RequestContext
from tools.repo_reader import fetch_dependencies
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_gradient import ChatGradient
from langchain_core.messages import SystemMessage, HumanMessage
from prompt import RESEARCHER_PROMPT
import os
import json
import re


search_tool = DuckDuckGoSearchRun()
llm = ChatGradient(model="openai-gpt-oss-120b")
# agent = create_tool_calling_agent(llm, [search_tool], RESEARCHER_PROMPT)
# executor = AgentExecutor(agent=agent, tools=[search_tool], verbose=True)


def _search_for_dep(dep_name: str) -> dict:
    # Step 1: use DuckDuckGo to get search results
    search_results = search_tool.run(f"{dep_name} official documentation quickstart")

    # Step 2: ask the LLM to pick the best URL from those results
    messages = [
        SystemMessage(content=RESEARCHER_PROMPT),
        HumanMessage(
            content=(
                f"Dependency: {dep_name}\n\n"
                f"Search results:\n{search_results}\n\n"
                f"Based on these results, return the JSON object."
            )
        ),
    ]

    response = llm.invoke(messages)
    raw = response.content.strip()

    # Strip Markdown fences if present
    raw = re.sub(r"^```json|^```|```$", "", raw, flags=re.MULTILINE).strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"name": dep_name, "url": None}


def find_doc_urls(dependencies: list[str]) -> list[dict]:
    """
    Takes a list of dependency names, returns a list of
    {"name": str, "url": str | None} dicts.
    """
    results = []
    for dep in dependencies:
        result = _search_for_dep(dep)
        results.append(result)
    return results


@entrypoint
async def main(payload: Dict[str, str], context: RequestContext):
    deps = fetch_dependencies(payload["repo_url"], os.getenv("GITHUB_TOKEN"))
    doc_urls = find_doc_urls(deps)
    return {
        "deps": doc_urls,
    }
