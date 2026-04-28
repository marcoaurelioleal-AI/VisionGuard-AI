import sqlite3
from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, UploadFile, status

from app.api.routes.general_detection import annotate_faces_and_objects
from app.core.config import (
    DEFAULT_CONFIDENCE_THRESHOLD,
    DEFAULT_FACE_MIN_NEIGHBORS,
    DEFAULT_FACE_MIN_SIZE,
    DEFAULT_FACE_SCALE_FACTOR,
)
from app.db.database import get_db
from app.schemas.analysis import AnalysisHistoryItem, ImageAnalysisResponse
from app.services.analysis_service import analysis_service
from app.services.class_filter_service import parse_class_filter
from app.services.face_detection_service import face_detection_service
from app.services.image_service import ImageService
from app.services.object_detection_service import object_detection_service

router = APIRouter(tags=["AI Analysis"])


@router.post(
    "/analyze/image",
    response_model=ImageAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
)
async def analyze_image(
    file: UploadFile = File(...),
    connection: sqlite3.Connection = Depends(get_db),
    confidence_threshold: Annotated[
        float,
        Query(
            ge=0,
            le=1,
            description="Minimum confidence required to return a YOLO detection.",
        ),
    ] = DEFAULT_CONFIDENCE_THRESHOLD,
    classes: Annotated[
        str | None,
        Query(
            description=(
                "Optional comma-separated YOLO labels to keep in the AI analysis. "
                "Example: person,car,dog."
            ),
        ),
    ] = None,
    scale_factor: Annotated[
        float,
        Query(
            gt=1.0,
            description="Image scale reduction factor used by OpenCV Haar Cascade.",
        ),
    ] = DEFAULT_FACE_SCALE_FACTOR,
    min_neighbors: Annotated[
        int,
        Query(
            ge=1,
            description="Minimum neighboring rectangles required for a face detection.",
        ),
    ] = DEFAULT_FACE_MIN_NEIGHBORS,
    min_size: Annotated[
        int,
        Query(
            ge=20,
            description="Minimum face size in pixels for OpenCV Haar Cascade.",
        ),
    ] = DEFAULT_FACE_MIN_SIZE,
) -> ImageAnalysisResponse:
    ImageService.validate_image_file(file)
    image_bytes = await ImageService.read_upload_file(file)
    image = ImageService.bytes_to_cv2_image(image_bytes)
    allowed_classes = parse_class_filter(classes)

    objects = object_detection_service.detect_objects(
        image,
        confidence_threshold=confidence_threshold,
        allowed_classes=allowed_classes,
    )
    faces = face_detection_service.detect_faces(
        image,
        scale_factor=scale_factor,
        min_neighbors=min_neighbors,
        min_size=min_size,
    )
    annotated_image = annotate_faces_and_objects(image, faces, objects)
    output_path = ImageService.save_annotated_image(annotated_image, file.filename)

    return analysis_service.save_analysis(
        connection=connection,
        filename=file.filename or "uploaded-image",
        faces=faces,
        objects=objects,
        output_path=output_path,
    )


@router.get("/analysis/history", response_model=list[AnalysisHistoryItem])
def list_analysis_history(
    connection: sqlite3.Connection = Depends(get_db),
    limit: Annotated[
        int,
        Query(ge=1, le=50, description="Maximum number of history records to return."),
    ] = 10,
) -> list[AnalysisHistoryItem]:
    return analysis_service.list_history(connection, limit=limit)
