import os

import httpx
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Project
from app.routes.events import notify_new_project

router = APIRouter(prefix="/projects", tags=["projects"])


class CreateProjectRequest(BaseModel):
    repo_url: str


class ProjectCallback(BaseModel):
    project_name: str
    repo_url: str
    site_url: str
    dependencies: List[str]
    status: str


class ProjectResponse(BaseModel):
    id: int
    project_name: str
    repo_url: str
    site_url: str
    dependencies: List[str]
    status: str

    class Config:
        from_attributes = True


async def trigger_agent(repo_url: str) -> None:
    """
    Runs in the background after /create returns 202.
    Calls the agent /run endpoint and lets the agent callback
    handle the rest on completion.
    """
    agent_url = os.getenv("AGENT_URL")
    if not agent_url:
        raise HTTPException(status_code=500, detail="Agent URL not set")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{agent_url}/run",
                json={"repo_url": repo_url},
                timeout=600,  # 10 min hard ceiling
            )
            response.raise_for_status()
            print(f"[agent] Pipeline completed for {repo_url}")
    except httpx.HTTPStatusError as exc:
        print(f"[agent] Pipeline failed with status {exc.response.status_code}: {exc}")
    except httpx.RequestError as exc:
        print(f"[agent] Could not reach agent: {exc}")


@router.post("/create", status_code=202)
async def create_project(
    payload: CreateProjectRequest,
    background_tasks: BackgroundTasks,
):
    """
    Accepts a repo_url, fires the agent pipeline in the background,
    and returns 202 immediately.
    The frontend should connect to /events/stream to receive
    the completion event when the agent finishes.
    """
    background_tasks.add_task(trigger_agent, payload.repo_url)
    return {"message": "Pipeline started", "repo_url": payload.repo_url}


@router.post("/callback", status_code=201)
async def project_callback(payload: ProjectCallback, db: Session = Depends(get_db)):
    """
    Called by the agent storer when a documentation site generation is complete.
    Creates the project in the database and pushes an SSE event to the frontend.
    """
    project = Project(
        project_name=payload.project_name,
        repo_url=payload.repo_url,
        site_url=payload.site_url,
        dependencies=payload.dependencies,
        status=payload.status,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    # Push SSE event so the frontend for immediate rerender
    await notify_new_project(
        {
            "id": project.id,
            "project_name": project.project_name,
            "site_url": project.site_url,
            "status": project.status,
        }
    )

    return {"id": project.id, "site_url": project.site_url}


@router.get("/", response_model=List[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    """
    Returns all projects, sorted by creation timestamp from latest to oldest.
    """
    return db.query(Project).order_by(Project.created_at.desc()).all()
