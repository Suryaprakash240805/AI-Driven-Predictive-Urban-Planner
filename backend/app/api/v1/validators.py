import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import date, datetime
from app.db.session import get_db
from app.models.project import Project, ProjectStatus
from app.models.validation import Validation, ValidationDecision
from app.models.user import User, UserRole
from app.schemas.validation import ApproveRequest, RejectRequest, ValidationOut, ValidatorStats
from app.dependencies import require_roles, get_current_user
from app.tasks.notification_task import send_user_notification, send_validator_notification
from app.tasks.layout_task import trigger_layout_generation
from geoalchemy2.shape import to_shape

router = APIRouter(prefix="/validators", tags=["validators"])

STAGE_ROLE_MAP = {
    UserRole.validator_1: 1,
    UserRole.validator_2: 2,
    UserRole.validator_3: 3,
}
NEXT_STAGE_ROLE_EMAIL = {
    1: "validator2@urbanplanner.in",
    2: "validator3@urbanplanner.in",
}

@router.get("/queue", response_model=list[dict])
async def get_pending_queue(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(
        "validator_1","validator_2","validator_3")),
):
    stage = STAGE_ROLE_MAP[current_user.role]
    # Projects at the correct stage with no existing validation record
    result = await db.execute(
        select(Project).where(
            Project.status == ProjectStatus.in_review,
            Project.current_stage == stage - 1,
        ).order_by(Project.created_at)
    )
    projects = result.scalars().all()
    return [
        {
            "id":         str(p.id),
            "name":       p.name,
            "city":       p.city,
            "use_type":   p.use_type,
            "land_info":  p.land_info,
            "created_at": p.created_at.isoformat(),
        }
        for p in projects
    ]

@router.post("/{project_id}/approve")
async def approve_project(
    project_id: uuid.UUID,
    body: ApproveRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(
        "validator_1","validator_2","validator_3")),
):
    project = (await db.execute(
        select(Project).where(Project.id == project_id)
    )).scalar_one_or_none()
    if not project:
        raise HTTPException(404, "Project not found")

    stage = STAGE_ROLE_MAP[current_user.role]
    validation = Validation(
        project_id=project_id, validator_id=current_user.id,
        stage=stage, decision=ValidationDecision.approved,
        feedback=body.feedback or "Approved.",
        validator_name=current_user.name,
    )
    db.add(validation)

    if stage == 3:
        # Final approval
        project.status        = ProjectStatus.approved_final
        project.current_stage = 3
    else:
        project.current_stage = stage

    await db.flush()

    # Post-approval actions
    if stage == 1:
        # Trigger AI layout generation
        polygon_geojson = {
            "type": "Feature",
            "geometry": {"type": "Polygon",
                         "coordinates": [list(to_shape(project.land_polygon).exterior.coords)]}
        }
        trigger_layout_generation.delay(
            str(project_id), polygon_geojson,
            project.land_info or {}, project.use_type,
        )

    if stage < 3:
        # Notify next validator
        send_validator_notification.delay(
            NEXT_STAGE_ROLE_EMAIL.get(stage, ""), project.name, stage + 1
        )

    # Notify user
    owner = (await db.execute(
        select(User).where(User.id == project.owner_id)
    )).scalar_one_or_none()
    if owner:
        send_user_notification.delay(
            owner.email, project.name, "approved", body.feedback or "", stage
        )

    return {"message": f"Project approved at Stage {stage}"}

@router.post("/{project_id}/reject")
async def reject_project(
    project_id: uuid.UUID,
    body: RejectRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(
        "validator_1","validator_2","validator_3")),
):
    project = (await db.execute(
        select(Project).where(Project.id == project_id)
    )).scalar_one_or_none()
    if not project:
        raise HTTPException(404, "Project not found")

    stage = STAGE_ROLE_MAP[current_user.role]
    validation = Validation(
        project_id=project_id, validator_id=current_user.id,
        stage=stage, decision=ValidationDecision.rejected,
        feedback=body.feedback, validator_name=current_user.name,
    )
    db.add(validation)
    project.status = ProjectStatus.rejected
    await db.flush()

    owner = (await db.execute(
        select(User).where(User.id == project.owner_id)
    )).scalar_one_or_none()
    if owner:
        send_user_notification.delay(
            owner.email, project.name, "rejected", body.feedback, stage
        )
    return {"message": f"Project rejected at Stage {stage}"}

@router.get("/stats", response_model=ValidatorStats)
async def get_validator_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(
        "validator_1","validator_2","validator_3")),
):
    stage     = STAGE_ROLE_MAP[current_user.role]
    today_str = date.today()

    total = (await db.execute(
        select(func.count()).select_from(Validation)
        .where(Validation.validator_id == current_user.id)
    )).scalar()

    approved_today = (await db.execute(
        select(func.count()).select_from(Validation)
        .where(Validation.validator_id == current_user.id,
               Validation.decision == ValidationDecision.approved,
               func.date(Validation.created_at) == today_str)
    )).scalar()

    rejected_today = (await db.execute(
        select(func.count()).select_from(Validation)
        .where(Validation.validator_id == current_user.id,
               Validation.decision == ValidationDecision.rejected,
               func.date(Validation.created_at) == today_str)
    )).scalar()

    pending = (await db.execute(
        select(func.count()).select_from(Project)
        .where(Project.status == ProjectStatus.in_review,
               Project.current_stage == stage - 1)
    )).scalar()

    return ValidatorStats(pending=pending, approved_today=approved_today,
                          rejected_today=rejected_today, total=total)
