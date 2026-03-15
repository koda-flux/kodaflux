from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Project
from app.routes.events import notify_new_project

router = APIRouter(prefix="/projects", tags=["projects"])


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
