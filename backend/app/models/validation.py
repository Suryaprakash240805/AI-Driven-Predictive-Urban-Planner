import uuid
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin
import enum

class ValidationDecision(str, enum.Enum):
    pending  = "pending"
    approved = "approved"
    rejected = "rejected"

class Validation(Base, TimestampMixin):
    __tablename__ = "validations"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id   = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    validator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"),    nullable=False)
    stage        = Column(Integer, nullable=False)       # 1, 2, or 3
    decision     = Column(SAEnum(ValidationDecision), default=ValidationDecision.pending)
    feedback     = Column(Text, nullable=True)
    validator_name = Column(String(120), nullable=True)  # denormalised for report

    project   = relationship("Project", back_populates="validations")
    validator = relationship("User",    back_populates="validations")
