import os
import uuid
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="Portfolio API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ProjectBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    description: str = Field(..., min_length=1, max_length=2000)
    tags: List[str] = Field(default_factory=list)


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=120)
    description: Optional[str] = Field(None, min_length=1, max_length=2000)
    tags: Optional[List[str]] = None


class Project(ProjectBase):
    id: str


# In-memory store (ephemeral)
PROJECTS: dict[str, Project] = {}


def seed_data() -> None:
    if PROJECTS:
        return
    examples = [
        Project(
            id=str(uuid.uuid4()),
            title="Midnight Dashboard",
            description="Clean analytics hub with high-contrast dark UI and buttery transitions.",
            tags=["React", "Framer Motion", "A11y"],
        ),
        Project(
            id=str(uuid.uuid4()),
            title="Aurora Docs",
            description="Documentation site with focus-first typography and instant search.",
            tags=["Content", "Search", "Dark Mode"],
        ),
        Project(
            id=str(uuid.uuid4()),
            title="Shadow Commerce",
            description="Performance-first storefront with snappy filters and crisp accents.",
            tags=["Performance", "UI/UX", "E-commerce"],
        ),
    ]
    for p in examples:
        PROJECTS[p.id] = p


seed_data()


@app.get("/")
def read_root():
    return {"message": "Portfolio API running"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/api/projects", response_model=List[Project])
def list_projects():
    return list(PROJECTS.values())


@app.post("/api/projects", response_model=Project, status_code=201)
def create_project(payload: ProjectCreate):
    pid = str(uuid.uuid4())
    project = Project(id=pid, **payload.dict())
    PROJECTS[pid] = project
    return project


@app.get("/api/projects/{project_id}", response_model=Project)
def get_project(project_id: str):
    project = PROJECTS.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.put("/api/projects/{project_id}", response_model=Project)
@app.patch("/api/projects/{project_id}", response_model=Project)
def update_project(project_id: str, payload: ProjectUpdate):
    project = PROJECTS.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    data = project.dict()
    updates = payload.dict(exclude_unset=True)
    data.update({k: v for k, v in updates.items() if v is not None})
    updated = Project(**data)
    PROJECTS[project_id] = updated
    return updated


@app.delete("/api/projects/{project_id}", status_code=204)
def delete_project(project_id: str):
    if project_id not in PROJECTS:
        raise HTTPException(status_code=404, detail="Project not found")
    del PROJECTS[project_id]
    return None


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
