from datetime import datetime
from sqlalchemy import String, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_name: Mapped[str] = mapped_column(String, index=True)
    repo_url: Mapped[str] = mapped_column(String)
    site_url: Mapped[str] = mapped_column(String)
    dependencies: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String, default=None, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
