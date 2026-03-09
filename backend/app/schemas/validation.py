from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.models.validation import ValidationDecision

class ApproveRequest(BaseModel):
    stage: int
    feedback: str | None = None

class RejectRequest(BaseModel):
    stage: int
    feedback: str

class ValidationOut(BaseModel):
    id: UUID
    project_id: UUID
    stage: int
    decision: ValidationDecision
    feedback: str | None
    validator_name: str | None
    created_at: datetime
    model_config = {"from_attributes": True}

class ValidatorStats(BaseModel):
    pending: int = 0
    approved_today: int = 0
    rejected_today: int = 0
    total: int = 0
