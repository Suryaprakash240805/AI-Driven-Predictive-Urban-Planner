import httpx
from app.config import settings

async def request_layout_generation(project_id: str, land_polygon: dict,
                                    land_info: dict, use_type: str) -> dict:
    """Call the ML microservice to generate 3 GNN layout options."""
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            f"{settings.ML_SERVICE_URL}/generate",
            json={
                "project_id":   project_id,
                "land_polygon": land_polygon,
                "land_info":    land_info,
                "use_type":     use_type,
            }
        )
        resp.raise_for_status()
        return resp.json()

async def get_layout_status(project_id: str) -> dict:
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(f"{settings.ML_SERVICE_URL}/status/{project_id}")
        resp.raise_for_status()
        return resp.json()
