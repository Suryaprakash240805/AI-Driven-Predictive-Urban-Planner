from fastapi import FastAPI
from ml.src.api.routes import router
from contextlib import asynccontextmanager
from ml.src.inference.predictor import load_model

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_model()   # warm up model at startup
    yield

app = FastAPI(title="Urban Planner ML Service",
              version="1.0.0", lifespan=lifespan)
app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok", "service": "urban-planner-ml"}
