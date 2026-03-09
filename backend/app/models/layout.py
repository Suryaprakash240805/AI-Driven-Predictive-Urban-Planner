import uuid
from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin

class Layout(Base, TimestampMixin):
    __tablename__ = "layouts"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id    = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    option_id     = Column(Integer, nullable=False)          # 1, 2, or 3
    strategy      = Column(String(50), nullable=False)       # maximize_builtup | maximize_green | balanced
    geojson       = Column(JSON, nullable=True)
    feasibility   = Column(Float, default=0.0)
    nbc_compliance= Column(Float, default=0.0)
    combined_score= Column(Float, default=0.0)
    image_url     = Column(String(500), nullable=True)       # MinIO URL
    is_selected   = Column(Boolean, default=False)

    project = relationship("Project", back_populates="layouts")
