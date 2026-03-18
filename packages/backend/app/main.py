from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.database import Base, engine
from app.routes import health, projects


load_dotenv()
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Kodaflux API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/healthz")
app.include_router(projects.router)
