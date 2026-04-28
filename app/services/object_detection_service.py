from typing import Any

import cv2
import numpy as np
from fastapi import HTTPException, status
from ultralytics import YOLO

from app.core.config import DEFAULT_CONFIDENCE_THRESHOLD, YOLO_MODEL_NAME, settings
from app.schemas.object import DetectedObject, ObjectBox


class ObjectDetectionService:
    def __init__(self, model_name: str = YOLO_MODEL_NAME) -> None:
        self.model_name = model_name
        self._model: YOLO | None = None

    @property
    def model(self) -> YOLO:
        if self._model is None:
            self._model = YOLO(self.model_name)

        return self._model

    def detect_objects(
        self,
        image: np.ndarray,
        confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
        allowed_classes: set[str] | None = None,
    ) -> list[DetectedObject]:
        try:
            results = self.model(
                image,
                imgsz=settings.yolo_image_size,
                verbose=False,
            )
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not run object detection model.",
            ) from exc

        return self._results_to_objects(results, confidence_threshold, allowed_classes)

    def detect_objects_with_annotations(
        self,
        image: np.ndarray,
        confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
        allowed_classes: set[str] | None = None,
    ) -> tuple[list[DetectedObject], np.ndarray]:
        objects = self.detect_objects(image, confidence_threshold, allowed_classes)
        annotated_image = image.copy()

        for detected_object in objects:
            self.draw_detection(annotated_image, detected_object)

        return objects, annotated_image

    def _results_to_objects(
        self,
        results: list[Any],
        confidence_threshold: float,
        allowed_classes: set[str] | None = None,
    ) -> list[DetectedObject]:
        detected_objects: list[DetectedObject] = []

        for result in results:
            class_names = result.names

            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                label = str(class_names[class_id])

                if confidence < confidence_threshold:
                    continue

                if allowed_classes is not None and label.lower() not in allowed_classes:
                    continue

                detected_objects.append(
                    DetectedObject(
                        label=label,
                        confidence=round(confidence, 2),
                        box=ObjectBox(
                            x1=max(0, int(x1)),
                            y1=max(0, int(y1)),
                            x2=max(0, int(x2)),
                            y2=max(0, int(y2)),
                        ),
                    )
                )

        return detected_objects

    @staticmethod
    def draw_detection(image: np.ndarray, detected_object: DetectedObject) -> None:
        box = detected_object.box
        label = f"{detected_object.label} {detected_object.confidence:.2f}"

        cv2.rectangle(
            image,
            (box.x1, box.y1),
            (box.x2, box.y2),
            color=(0, 255, 0),
            thickness=2,
        )
        cv2.putText(
            image,
            label,
            (box.x1, max(20, box.y1 - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )


object_detection_service = ObjectDetectionService()
