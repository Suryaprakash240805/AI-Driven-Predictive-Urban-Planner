import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import io
from app.db.session import get_db
from app.models.project import Project
from app.models.report import Report
from app.models.layout import Layout
from app.models.validation import Validation
from app.models.user import User
from app.schemas.report import ReportOut
from app.services.report_service import generate_project_pdf
from app.services.storage_service import upload_pdf, get_object_bytes
from app.dependencies import get_current_user
from app.config import settings

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/{project_id}", response_model=dict)
async def get_report(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = (await db.execute(
        select(Project).where(Project.id == project_id)
    )).scalar_one_or_none()
    if not project:
        raise HTTPException(404, "Project not found")

    validations = (await db.execute(
        select(Validation).where(Validation.project_id == project_id)
        .order_by(Validation.stage)
    )).scalars().all()

    selected_layout = (await db.execute(
        select(Layout).where(Layout.project_id == project_id,
                             Layout.is_selected == True)
    )).scalar_one_or_none()

    owner = (await db.execute(
        select(User).where(User.id == project.owner_id)
    )).scalar_one_or_none()

    return {
        "id":              str(project.id),
        "name":            project.name,
        "city":            project.city,
        "state":           project.state,
        "use_type":        project.use_type,
        "status":          project.status,
        "land_info":       project.land_info,
        "owner_name":      owner.name if owner else "—",
        "validations":     [
            {
                "stage":          v.stage,
                "decision":       v.decision,
                "feedback":       v.feedback,
                "validator_name": v.validator_name,
                "created_at":     v.created_at.isoformat(),
            }
            for v in validations
        ],
        "selected_layout": {
            "option_id":      selected_layout.option_id,
            "strategy":       selected_layout.strategy,
            "feasibility":    selected_layout.feasibility,
            "nbc_compliance": selected_layout.nbc_compliance,
            "combined_score": selected_layout.combined_score,
            "image_url":      selected_layout.image_url,
        } if selected_layout else None,
    }

@router.get("/{project_id}/download")
async def download_report(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report_data = await get_report(project_id, db, current_user)
    pdf_bytes   = generate_project_pdf(
        report_data,
        report_data.get("validations", []),
        report_data.get("selected_layout"),
        None,
    )
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=report_{project_id}.pdf"},
    )

@router.get("/{project_id}/layout")
async def download_layout(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    selected = (await db.execute(
        select(Layout).where(Layout.project_id == project_id,
                             Layout.is_selected == True)
    )).scalar_one_or_none()
    if not selected or not selected.image_url:
        raise HTTPException(404, "Layout image not found")

    filename = selected.image_url.split("/")[-1]
    img_bytes = get_object_bytes(settings.MINIO_BUCKET_LAYOUTS, filename)
    return StreamingResponse(
        io.BytesIO(img_bytes),
        media_type="image/png",
        headers={"Content-Disposition": f"attachment; filename=layout_{project_id}.png"},
    )
