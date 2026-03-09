from fastapi import APIRouter
from app.api.v1 import auth, projects, land, layouts, validators, reports

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(projects.router)
api_router.include_router(land.router)
api_router.include_router(layouts.router)
api_router.include_router(validators.router)
api_router.include_router(reports.router)
