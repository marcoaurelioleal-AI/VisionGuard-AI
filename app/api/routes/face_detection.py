from typing import Annotated

from fastapi import APIRouter, File, Query, UploadFile, status

from app.core.config import (
    DEFAULT_FACE_MIN_NEIGHBORS,
    DEFAULT_FACE_MIN_SIZE,
    DEFAULT_FACE_SCALE_FACTOR,
)
from app.schemas.face import AnnotatedFaceResponse, FaceDetectionResponse
from app.services.face_detection_service import face_detection_service
from app.services.image_service import ImageService

router = APIRouter(prefix="/detect", tags=["Face Detection"])


@router.post(
    "/faces",
    response_model=FaceDetectionResponse,
    status_code=status.HTTP_200_OK,
)
async def detect_faces(
    file: UploadFile = File(...),
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
) -> FaceDetectionResponse:
    ImageService.validate_image_file(file)
    image_bytes = await ImageService.read_upload_file(file)
    image = ImageService.bytes_to_cv2_image(image_bytes)
    faces = face_detection_service.detect_faces(
        image,
        scale_factor=scale_factor,
        min_neighbors=min_neighbors,
        min_size=min_size,
    )

    return FaceDetectionResponse(total_faces=len(faces), faces=faces)


@router.post(
    "/faces/annotated",
    response_model=AnnotatedFaceResponse,
    status_code=status.HTTP_200_OK,
)
async def detect_faces_annotated(
    file: UploadFile = File(...),
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
) -> AnnotatedFaceResponse:
    ImageService.validate_image_file(file)
    image_bytes = await ImageService.read_upload_file(file)
    image = ImageService.bytes_to_cv2_image(image_bytes)
    faces, annotated_image = face_detection_service.detect_faces_with_annotations(
        image,
        scale_factor=scale_factor,
        min_neighbors=min_neighbors,
        min_size=min_size,
    )
    output_path = ImageService.save_annotated_image(annotated_image, file.filename)

    return AnnotatedFaceResponse(
        message="Annotated face image created successfully",
        output_path=output_path,
        total_faces=len(faces),
    )
