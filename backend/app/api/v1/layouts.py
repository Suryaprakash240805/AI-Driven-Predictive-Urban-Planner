import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from geoalchemy2.shape import to_shape
from app.db.session import get_db
from app.models.project import Project
from app.models.layout import Layout
from app.schemas.layout import LayoutsResponse, SelectLayoutRequest, LayoutOptionOut
from app.dependencies import get_current_user, require_roles
from app.models.user import User
from app.tasks.layout_task import trigger_layout_generation

router = APIRouter(prefix="/layouts", tags=["layouts"])

@router.post("/generate/{project_id}", response_model=LayoutsResponse)
async def generate_layouts(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("citizen","validator_1","validator_2","validator_3")),
):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(404, "Project not found")

    # Check for cached layouts first
    existing = await db.execute(select(Layout).where(Layout.project_id == project_id))
    layouts  = existing.scalars().all()
    if layouts:
        return {"project_id": project_id, "options": layouts}

    # Trigger async ML generation
    polygon_geojson = {"type": "Feature",
                       "geometry": {"type": "Polygon",
                                    "coordinates": [list(to_shape(project.land_polygon).exterior.coords)]}}
    trigger_layout_generation.delay(
        str(project_id), polygon_geojson,
        project.land_info or {}, project.use_type,
    )

    # Return mock layouts immediately (real ones come via WebSocket)
    mock_options = _mock_layouts(project_id)
    for opt in mock_options:
        db.add(Layout(project_id=project_id, **opt))
    await db.flush()

    new_layouts = (await db.execute(
        select(Layout).where(Layout.project_id == project_id)
    )).scalars().all()
    return {"project_id": project_id, "options": new_layouts}

@router.post("/select/{project_id}")
async def select_layout(
    project_id: uuid.UUID,
    body: SelectLayoutRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("citizen")),
):
    # Deselect all first
    await db.execute(update(Layout).where(Layout.project_id == project_id)
                     .values(is_selected=False))
    # Select chosen option
    await db.execute(update(Layout)
                     .where(Layout.project_id == project_id,
                            Layout.option_id == body.option)
                     .values(is_selected=True))
    return {"message": "Layout selected successfully", "option": body.option}

def _mock_layouts(project_id) -> list[dict]:
    return [
        {"option_id":1,"strategy":"maximize_builtup","feasibility":0.87,
         "nbc_compliance":0.82,"combined_score":0.85,"geojson":None,"image_url":None},
        {"option_id":2,"strategy":"maximize_green","feasibility":0.79,
         "nbc_compliance":0.94,"combined_score":0.85,"geojson":None,"image_url":None},
        {"option_id":3,"strategy":"balanced","feasibility":0.83,
         "nbc_compliance":0.88,"combined_score":0.85,"geojson":None,"image_url":None},
    ]
