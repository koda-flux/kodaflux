import os
import re
import tomllib
import json
import base64
from typing import Callable, List

from github import Github, GithubException, Repository
from langchain_core.tools import tool


def _parse_requirements(content: str) -> list[str]:
    """
    Handles requirements.txt, requirements-dev.txt, etc.
    Strips version specifiers, extras, and VCS/URL entries.
    """
    deps: list[str] = []
    for raw_line in content.splitlines():
        line = raw_line.strip()

        # skip blanks, comments, flags (-r, -c, -e, --index-url …)
        if not line or line.startswith(("#", "-")):
            continue

        # skip VCS / URL requirements (git+https://, https://, …)
        if re.match(r"^\w+\+https?://|^https?://", line):
            continue

        # normalise: drop inline comments
        line = line.split("#")[0].strip()

        # strip extras [security], version specifiers (==, >=, <=, ~=, !=, >)
        name = re.split(r"[><=!~;\[]", line)[0].strip()
        if name:
            deps.append(name)
    print(deps)
    return deps


def _parse_pyproject(content: str) -> list[str]:
    """
    Supports PEP 621 [project.dependencies], Poetry
    [tool.poetry.dependencies], and PDM/Hatch/Flit via the same PEP 621 key.
    """
    try:
        data = tomllib.loads(content)
    except Exception:
        return []

    deps: list[str] = []

    for raw in data.get("project", {}).get("dependencies", []):
        name = re.split(r"[><=!~;\[]", str(raw))[0].strip()
        if name:
            deps.append(name)

    for group in data.get("project", {}).get("optional-dependencies", {}).values():
        for raw in group:
            name = re.split(r"[><=!~;\[]", str(raw))[0].strip()
            if name:
                deps.append(name)

    # Poetry — dependencies are a dict { name: version-constraint }
    poetry_deps: dict = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
    for name in poetry_deps:
        if name.lower() != "python":
            deps.append(name)

    # Poetry dev / group dependencies
    for group in data.get("tool", {}).get("poetry", {}).get("group", {}).values():
        for name in group.get("dependencies", {}):
            if name.lower() != "python":
                deps.append(name)

    # Legacy Poetry dev-dependencies
    for name in data.get("tool", {}).get("poetry", {}).get("dev-dependencies", {}):
        if name.lower() != "python":
            deps.append(name)

    return deps


def _parse_package_json(content: str) -> List[str]:
    """
    Reads dependencies, devDependencies, and peerDependencies.
    Skips workspace protocol entries and local file: paths.
    """
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return []

    names: List[str] = []
    for key in ("dependencies", "devDependencies", "peerDependencies"):
        for name, version in data.get(key, {}).items():
            version_str = str(version)
            # skip workspace references and local paths
            if version_str.startswith(("workspace:", "file:", "link:")):
                continue
            names.append(name)

    return names


PARSERS: dict[str, Callable[[str], list[str]]] = {
    "requirements.txt": _parse_requirements,
    "pyproject.toml": _parse_pyproject,
    "package.json": _parse_package_json,
}

TARGET_FILENAMES: set[str] = set(PARSERS.keys())


def _parse_owner_repo(repo_url: str) -> tuple[str, str]:
    """'https://github.com/owner/repo' → ('owner', 'repo')"""
    clean = repo_url.rstrip("/").removeprefix("https://github.com/")
    owner, repo = clean.split("/")[:2]
    return owner, repo


def _decode_file_content(encoded: str) -> str:
    """GitHub API returns base-64 content with newlines — strip and decode."""
    return base64.b64decode(encoded.replace("\n", "")).decode("utf-8")


def _get_dep_file_paths(repo: Repository) -> list[str]:
    """
    Uses the Git Trees API (recursive=True) for a single round-trip
    to get every file path in the repo, then filters to dep files.
    """
    try:
        tree = repo.get_git_tree(sha="HEAD", recursive=True)
    except GithubException as exc:
        raise RuntimeError(f"Could not fetch git tree: {exc}") from exc

    return [
        item.path
        for item in tree.tree
        if item.type == "blob" and item.path.split("/")[-1] in TARGET_FILENAMES
    ]


def fetch_dependencies(repo_url: str, github_token: str | None = None) -> List[str]:
    """
    Given a public GitHub repo URL, returns a sorted list of unique
    dependency names found across all requirements.txt, pyproject.toml,
    and package.json files in the repository (including subdirectories).

    Args:
        repo_url:      Full GitHub URL, e.g. "https://github.com/owner/repo"
        github_token:  Optional PAT — raises rate limits from 60 to 5000 req/hr.

    Returns:
        Sorted list of unique dependency name strings.
    """
    g = Github(github_token)
    owner, repo_name = _parse_owner_repo(repo_url)

    try:
        repo = g.get_repo(f"{owner}/{repo_name}")
    except GithubException as exc:
        raise RuntimeError(
            f"Could not fetch repo '{owner}/{repo_name}': {exc}"
        ) from exc

    dep_file_paths = _get_dep_file_paths(repo)
    all_deps: set[str] = set()

    for path in dep_file_paths:
        filename = path.split("/")[-1]
        parser = PARSERS.get(filename)
        if not parser:
            continue

        try:
            file_obj = repo.get_contents(path)
            # get_contents returns a list if path is a directory — skip that
            if isinstance(file_obj, list):
                continue
            raw_content = _decode_file_content(file_obj.content)
            deps = parser(raw_content)
            all_deps.update(deps)
        except GithubException:
            continue  # file disappeared between tree fetch and read — skip
        except Exception:
            continue  # malformed file — skip silently

    g.close()
    return sorted(all_deps, key=str.lower)


@tool
def github_repo_dependencies(repo_url: str) -> list[str]:
    """
    Fetches all dependencies from a GitHub repository by reading
    requirements.txt, pyproject.toml, and package.json files
    found anywhere in the repo tree.

    Args:
        repo_url: Full GitHub URL e.g. https://github.com/owner/repo

    Returns:
        Sorted list of unique dependency name strings.
    """
    return fetch_dependencies(repo_url, github_token=os.getenv("GITHUB_TOKEN"))
