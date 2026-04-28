from pydantic import BaseModel, Field


class ObjectBox(BaseModel):
    x1: int = Field(..., ge=0)
    y1: int = Field(..., ge=0)
    x2: int = Field(..., ge=0)
    y2: int = Field(..., ge=0)


class DetectedObject(BaseModel):
    label: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    box: ObjectBox


class ObjectDetectionResponse(BaseModel):
    total_objects: int = Field(..., ge=0)
    objects: list[DetectedObject]


class AnnotatedObjectDetectionResponse(BaseModel):
    message: str
    output_path: str
    total_objects: int = Field(..., ge=0)
    objects: list[DetectedObject] = Field(default_factory=list)
