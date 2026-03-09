from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.services.gee_service import analyze_land_polygon, init_gee
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/land", tags=["land"])

class LandAnalyzeRequest(BaseModel):
    polygon: dict  # GeoJSON Feature or Geometry

@router.post("/analyze")
async def analyze_land(
    body: LandAnalyzeRequest,
    current_user: User = Depends(get_current_user),
):
    result = await analyze_land_polygon(body.polygon)
    return result
