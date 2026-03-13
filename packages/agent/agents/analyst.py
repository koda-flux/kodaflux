import os
import re
import json

from langchain_gradient import ChatGradient
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent

from state import AgentState
from .prompts import ANALYST_PROMPTS
from tools.repo_reader import github_repo_dependencies


model = ChatGradient(model=os.getenv("DIGITALOCEAN_INFERENCE_MODEL"))
agent = create_react_agent(
    model=model,
    tools=[github_repo_dependencies],
    prompt=ANALYST_PROMPTS["system"],
)


async def analyst(state: AgentState) -> AgentState:
    repo_url = state.get("repo_url")
    result = await agent.ainvoke(
        {"messages": [HumanMessage(content=ANALYST_PROMPTS["user"].format(repo_url))]}
    )

    raw_content = result["messages"][-1].content
    raw = re.sub(r"^```json|^```|```$", "", raw_content, flags=re.MULTILINE).strip()

    try:
        dependencies = json.loads(raw)
        if not isinstance(dependencies, list):
            dependencies = []
    except json.JSONDecodeError:
        dependencies = []

    return {**state, "dependencies": dependencies}
