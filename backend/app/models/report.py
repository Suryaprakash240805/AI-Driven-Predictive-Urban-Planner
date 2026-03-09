import uuid
from sqlalchemy import Column, String, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin

class Report(Base, TimestampMixin):
    __tablename__ = "reports"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id  = Column(UUID(as_uuid=True), ForeignKey("projects.id"), unique=True)
    pdf_url     = Column(String(500), nullable=True)
    layout_url  = Column(String(500), nullable=True)
    validator_signatures = Column(JSON, nullable=True)   # [{name, role, timestamp}]
    meta        = Column(JSON, nullable=True)
