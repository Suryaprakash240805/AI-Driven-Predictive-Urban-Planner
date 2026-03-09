from pydantic import BaseModel
from uuid import UUID
from typing import Any
from datetime import datetime
from app.models.project import ProjectStatus, UseType

class ProjectCreate(BaseModel):
    name: str | None = None
    use_type: UseType
    land_polygon: dict        # GeoJSON Feature
    land_info: dict | None = None
    city: str | None = None
    state: str | None = None

class ProjectOut(BaseModel):
    id: UUID
    name: str
    use_type: UseType
    status: ProjectStatus
    current_stage: int
    city: str | None
    state: str | None
    land_info: dict | None
    created_at: datetime
    model_config = {"from_attributes": True}

class ProjectDetail(ProjectOut):
    validations: list[Any] = []
    layouts: list[Any] = []
