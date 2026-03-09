import torch
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from ml.src.inference.predictor import load_model
from ml.src.inference.layout_generator import generate_options
from ml.src.services.storage_service import upload_layout_image

router = APIRouter()

class GenerateRequest(BaseModel):
    project_id:   str
    land_polygon: dict
    land_info:    dict
    use_type:     str

class StatusResponse(BaseModel):
    project_id: str
    status:     str
    options:    list | None = None

_job_store: dict = {}   # In-memory; replace with Redis in production

@router.post("/generate")
async def generate(req: GenerateRequest, bg: BackgroundTasks):
    _job_store[req.project_id] = {"status": "processing", "options": None}
    bg.add_task(_run_generation, req)
    return {"project_id": req.project_id, "status": "processing"}

async def _run_generation(req: GenerateRequest):
    try:
        device  = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model   = load_model()
        options = generate_options(req.land_polygon, req.use_type, model, device)

        for opt in options:
            img_path = opt.pop("image_path", None)
            if img_path:
                try:
                    with open(img_path, "rb") as f:
                        img_bytes = f.read()
                    fname = f"layout_{req.project_id}_opt{opt['option_id']}.png"
                    opt["image_url"] = upload_layout_image(img_bytes, fname)
                except Exception:
                    opt["image_url"] = None

        _job_store[req.project_id] = {"status": "done", "options": options}
    except Exception as e:
        _job_store[req.project_id] = {"status": "error", "options": None, "error": str(e)}

@router.get("/status/{project_id}", response_model=StatusResponse)
def get_status(project_id: str):
    job = _job_store.get(project_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return StatusResponse(project_id=project_id, **job)
