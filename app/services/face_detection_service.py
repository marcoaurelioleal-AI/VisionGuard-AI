import cv2
import numpy as np
from fastapi import HTTPException, status

from app.core.config import (
    DEFAULT_FACE_MIN_NEIGHBORS,
    DEFAULT_FACE_MIN_SIZE,
    DEFAULT_FACE_SCALE_FACTOR,
)
from app.schemas.face import FaceBox


class FaceDetectionService:
    def __init__(self) -> None:
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

        if self.face_cascade.empty():
            raise RuntimeError("Could not load OpenCV Haar Cascade model.")

    def detect_faces(
        self,
        image: np.ndarray,
        scale_factor: float = DEFAULT_FACE_SCALE_FACTOR,
        min_neighbors: int = DEFAULT_FACE_MIN_NEIGHBORS,
        min_size: int = DEFAULT_FACE_MIN_SIZE,
    ) -> list[FaceBox]:
        try:
            grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            detected_faces = self.face_cascade.detectMultiScale(
                grayscale_image,
                scaleFactor=scale_factor,
                minNeighbors=min_neighbors,
                minSize=(min_size, min_size),
            )
        except cv2.error as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not process image for face detection.",
            ) from exc

        return [
            FaceBox(x=int(x), y=int(y), width=int(width), height=int(height))
            for x, y, width, height in detected_faces
        ]

    def detect_faces_with_annotations(
        self,
        image: np.ndarray,
        scale_factor: float = DEFAULT_FACE_SCALE_FACTOR,
        min_neighbors: int = DEFAULT_FACE_MIN_NEIGHBORS,
        min_size: int = DEFAULT_FACE_MIN_SIZE,
    ) -> tuple[list[FaceBox], np.ndarray]:
        faces = self.detect_faces(
            image,
            scale_factor=scale_factor,
            min_neighbors=min_neighbors,
            min_size=min_size,
        )
        annotated_image = image.copy()

        for face in faces:
            self.draw_face_box(annotated_image, face)

        return faces, annotated_image

    @staticmethod
    def draw_face_box(image: np.ndarray, face: FaceBox) -> None:
        cv2.rectangle(
            image,
            (face.x, face.y),
            (face.x + face.width, face.y + face.height),
            color=(255, 0, 0),
            thickness=2,
        )
        cv2.putText(
            image,
            "face",
            (face.x, max(20, face.y - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 0, 0),
            2,
            cv2.LINE_AA,
        )


face_detection_service = FaceDetectionService()
