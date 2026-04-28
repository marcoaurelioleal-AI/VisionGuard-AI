from fastapi import FastAPI

from app.api.routes import (
    analysis,
    face_detection,
    general_detection,
    health,
    object_detection,
)
from app.core.config import settings
from app.core.rate_limiter import rate_limit_heavy_endpoints
from app.db.database import init_db

init_db()

app = FastAPI(
    title=settings.app_name,
    description="API for face and object detection using FastAPI, OpenCV and YOLO.",
    version="0.1.0",
)

app.middleware("http")(rate_limit_heavy_endpoints)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "VisionGuard API is running"}


app.include_router(health.router)
app.include_router(face_detection.router)
app.include_router(object_detection.router)
app.include_router(general_detection.router)
app.include_router(analysis.router)
