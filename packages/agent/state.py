from typing import TypedDict, Optional


class DepInfo(TypedDict):
    name: str
    doc_url: Optional[str]
    markdown: Optional[str]


class AgentState(TypedDict):
    repo_url: str
    project_name: str
    dependencies: list[str]
    dep_infos: list[DepInfo]
    stored: bool
    error: Optional[str]
