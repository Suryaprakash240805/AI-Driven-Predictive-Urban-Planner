import json, uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from geoalchemy2.shape import from_shape
from shapely.geometry import shape
from app.db.session import get_db
from app.models.project import Project, ProjectStatus
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectOut, ProjectDetail
from app.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("", response_model=ProjectOut, status_code=201)
async def create_project(
    body: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("citizen")),
):
    geo_shape  = shape(body.land_polygon.get("geometry", body.land_polygon))
    polygon_wkb = from_shape(geo_shape, srid=4326)
    name = body.name or f"{current_user.name}'s {body.use_type.replace('_',' ').title()}"
    project = Project(
        name=name, owner_id=current_user.id,
        use_type=body.use_type, status=ProjectStatus.in_review,
        land_polygon=polygon_wkb,
        land_info=body.land_info,
        city=body.city or current_user.city,
        state=body.state or current_user.state,
    )
    db.add(project)
    await db.flush()

    # Notify validator_1 (Celery task)
    from app.tasks.notification_task import send_validator_notification
    send_validator_notification.delay("validator1@urbanplanner.in", project.name, 1)
    return project

@router.get("/mine", response_model=list[ProjectOut])
async def get_my_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Project).where(Project.owner_id == current_user.id)
        .order_by(Project.created_at.desc())
    )
    return result.scalars().all()

@router.get("/{project_id}", response_model=ProjectDetail)
async def get_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(404, "Project not found")
    if project.owner_id != current_user.id and not current_user.role.startswith("validator"):
        raise HTTPException(403, "Access denied")
    return project
