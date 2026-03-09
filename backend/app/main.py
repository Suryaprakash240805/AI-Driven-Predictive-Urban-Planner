from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.router import api_router
from app.api.v1.websocket import router as ws_router
from app.db.base import Base
from app.db.session import engine
from app.services.gee_service import init_gee
from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    init_gee()
    yield
    # Shutdown
    await engine.dispose()

app = FastAPI(
    title="Urban Planner API",
    version="1.0.0",
    description="AI-Powered Land Planning for Tier-2 & Tier-3 Cities in India",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(ws_router)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "urban-planner-backend",
            "env": settings.APP_ENV}
