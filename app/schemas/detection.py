from pydantic import BaseModel, Field

from app.schemas.face import FaceBox
from app.schemas.object import DetectedObject


class CombinedDetectionResponse(BaseModel):
    total_faces: int = Field(..., ge=0)
    total_objects: int = Field(..., ge=0)
    faces: list[FaceBox]
    objects: list[DetectedObject]


class AnnotatedCombinedDetectionResponse(BaseModel):
    message: str
    output_path: str
    total_faces: int = Field(..., ge=0)
    total_objects: int = Field(..., ge=0)
    faces: list[FaceBox] = Field(default_factory=list)
    objects: list[DetectedObject] = Field(default_factory=list)
