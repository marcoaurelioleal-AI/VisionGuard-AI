from pydantic import BaseModel, Field


class FaceBox(BaseModel):
    x: int = Field(..., ge=0)
    y: int = Field(..., ge=0)
    width: int = Field(..., ge=0)
    height: int = Field(..., ge=0)


class FaceDetectionResponse(BaseModel):
    total_faces: int = Field(..., ge=0)
    faces: list[FaceBox]


class AnnotatedFaceResponse(BaseModel):
    message: str
    output_path: str
    total_faces: int = Field(..., ge=0)
