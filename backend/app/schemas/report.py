from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class ReportOut(BaseModel):
    id: UUID
    project_id: UUID
    pdf_url: str | None
    layout_url: str | None
    validator_signatures: list | None
    created_at: datetime
    model_config = {"from_attributes": True}
