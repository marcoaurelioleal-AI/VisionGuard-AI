from typing import Annotated

from fastapi import APIRouter, File, Query, UploadFile, status

from app.core.config import DEFAULT_CONFIDENCE_THRESHOLD
from app.schemas.object import (
    AnnotatedObjectDetectionResponse,
    ObjectDetectionResponse,
)
from app.services.class_filter_service import parse_class_filter
from app.services.image_service import ImageService
from app.services.object_detection_service import object_detection_service

router = APIRouter(prefix="/detect", tags=["Object Detection"])


@router.post(
    "/objects",
    response_model=ObjectDetectionResponse,
    status_code=status.HTTP_200_OK,
)
async def detect_objects(
    file: UploadFile = File(...),
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
                "Optional comma-separated YOLO labels to keep. "
                "Example: person,car,dog."
            ),
        ),
    ] = None,
) -> ObjectDetectionResponse:
    ImageService.validate_image_file(file)
    image_bytes = await ImageService.read_upload_file(file)
    image = ImageService.bytes_to_cv2_image(image_bytes)
    allowed_classes = parse_class_filter(classes)
    objects = object_detection_service.detect_objects(
        image,
        confidence_threshold,
        allowed_classes,
    )

    return ObjectDetectionResponse(total_objects=len(objects), objects=objects)


@router.post(
    "/objects/annotated",
    response_model=AnnotatedObjectDetectionResponse,
    status_code=status.HTTP_200_OK,
)
async def detect_objects_annotated(
    file: UploadFile = File(...),
    confidence_threshold: Annotated[
        float,
        Query(
            ge=0,
            le=1,
            description="Minimum confidence required to return and draw YOLO detections.",
        ),
    ] = DEFAULT_CONFIDENCE_THRESHOLD,
    classes: Annotated[
        str | None,
        Query(
            description=(
                "Optional comma-separated YOLO labels to return and draw. "
                "Example: person,car,dog."
            ),
        ),
    ] = None,
) -> AnnotatedObjectDetectionResponse:
    ImageService.validate_image_file(file)
    image_bytes = await ImageService.read_upload_file(file)
    image = ImageService.bytes_to_cv2_image(image_bytes)

    allowed_classes = parse_class_filter(classes)
    objects, annotated_image = object_detection_service.detect_objects_with_annotations(
        image,
        confidence_threshold,
        allowed_classes,
    )
    output_path = ImageService.save_annotated_image(annotated_image, file.filename)

    return AnnotatedObjectDetectionResponse(
        message="Annotated image created successfully",
        output_path=output_path,
        total_objects=len(objects),
        objects=objects,
    )
