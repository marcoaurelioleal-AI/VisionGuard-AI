from pydantic import BaseModel, Field

from app.schemas.face import FaceBox
from app.schemas.object import DetectedObject


class ImageAnalysisResponse(BaseModel):
    id: int
    filename: str
    summary: str
    risk_level: str
    detected_context: str
    recommendations: list[str]
    total_faces: int = Field(..., ge=0)
    total_objects: int = Field(..., ge=0)
    average_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    output_path: str | None = None
    faces: list[FaceBox]
    objects: list[DetectedObject]


class AnalysisHistoryItem(BaseModel):
    id: int
    filename: str
    summary: str
    risk_level: str
    detected_context: str
    total_faces: int = Field(..., ge=0)
    total_objects: int = Field(..., ge=0)
    average_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    output_path: str | None = None
    created_at: str
