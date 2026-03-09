import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, Enum as SAEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.db.base import Base, TimestampMixin
import enum

class ProjectStatus(str, enum.Enum):
    draft       = "draft"
    in_review   = "in_review"
    approved    = "approved"
    rejected    = "rejected"
    approved_final = "approved_final"

class UseType(str, enum.Enum):
    personal_residence  = "personal_residence"
    commercial_complex  = "commercial_complex"
    residential_complex = "residential_complex"

class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name          = Column(String(200), nullable=False)
    owner_id      = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    use_type      = Column(SAEnum(UseType), nullable=False)
    status        = Column(SAEnum(ProjectStatus), default=ProjectStatus.draft, nullable=False)
    current_stage = Column(Integer, default=0)
    city          = Column(String(100), nullable=True)
    state         = Column(String(100), nullable=True)

    # PostGIS geometry field for land polygon
    land_polygon  = Column(Geometry(geometry_type="POLYGON", srid=4326), nullable=True)
    land_info     = Column(JSON, nullable=True)   # NDVI, slope, elevation, etc.

    owner       = relationship("User",       back_populates="projects")
    validations = relationship("Validation", back_populates="project", lazy="selectin",
                               order_by="Validation.stage")
    layouts     = relationship("Layout",     back_populates="project", lazy="selectin")
