import uuid
from sqlalchemy import Column, String, Boolean, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin
import enum

class UserRole(str, enum.Enum):
    citizen     = "citizen"
    validator_1 = "validator_1"
    validator_2 = "validator_2"
    validator_3 = "validator_3"

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id       = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name     = Column(String(120), nullable=False)
    email    = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role     = Column(SAEnum(UserRole), nullable=False, default=UserRole.citizen)
    city     = Column(String(100), nullable=True)
    state    = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    projects    = relationship("Project",    back_populates="owner",  lazy="selectin")
    validations = relationship("Validation", back_populates="validator", lazy="selectin")
