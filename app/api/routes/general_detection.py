from typing import Annotated

from fastapi import APIRouter, File, Query, UploadFile, status

from app.core.config import (
    DEFAULT_CONFIDENCE_THRESHOLD,
    DEFAULT_FACE_MIN_NEIGHBORS,
    DEFAULT_FACE_MIN_SIZE,
    DEFAULT_FACE_SCALE_FACTOR,
)
from app.schemas.detection import (
    AnnotatedCombinedDetectionResponse,
    CombinedDetectionResponse,
)
from app.services.class_filter_service import parse_class_filter
from app.services.face_detection_service import face_detection_service
from app.services.image_service import ImageService
from app.services.object_detection_service import object_detection_service

router = APIRouter(prefix="/detect", tags=["General Detection"])


def annotate_faces_and_objects(image, faces, objects):
    annotated_image = image.copy()

    for detected_object in objects:
        object_detection_service.draw_detection(annotated_image, detected_object)

    for face in faces:
        face_detection_service.draw_face_box(annotated_image, face)

    return annotated_image


@router.post(
    "/all",
    response_model=CombinedDetectionResponse,
    status_code=status.HTTP_200_OK,
)
async def detect_all(
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
) -> CombinedDetectionResponse:
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

    return CombinedDetectionResponse(
        total_faces=len(faces),
        total_objects=len(objects),
        faces=faces,
        objects=objects,
    )


@router.post(
    "/all/annotated",
    response_model=AnnotatedCombinedDetectionResponse,
    status_code=status.HTTP_200_OK,
)
async def detect_all_annotated(
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
                "Optional comma-separated YOLO labels to return and draw. "
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
) -> AnnotatedCombinedDetectionResponse:
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

    return AnnotatedCombinedDetectionResponse(
        message="Annotated combined image created successfully",
        output_path=output_path,
        total_faces=len(faces),
        total_objects=len(objects),
        faces=faces,
        objects=objects,
    )
