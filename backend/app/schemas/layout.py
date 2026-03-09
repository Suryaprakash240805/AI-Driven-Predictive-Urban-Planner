from pydantic import BaseModel
from uuid import UUID

class LayoutOptionOut(BaseModel):
    option_id: int
    strategy: str
    feasibility: float
    nbc_compliance: float
    combined_score: float
    geojson: dict | None = None
    image_url: str | None = None
    model_config = {"from_attributes": True}

class LayoutsResponse(BaseModel):
    project_id: UUID
    options: list[LayoutOptionOut]

class SelectLayoutRequest(BaseModel):
    option: int
