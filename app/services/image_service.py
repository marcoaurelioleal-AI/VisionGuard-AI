from pathlib import Path
from uuid import uuid4

import cv2
import numpy as np
from fastapi import HTTPException, UploadFile, status

from app.core.config import settings

UPLOAD_READ_CHUNK_SIZE = 1024 * 1024


class ImageService:
    @staticmethod
    def is_allowed_image_extension(filename: str | None) -> bool:
        if not filename:
            return False

        return Path(filename).suffix.lower() in settings.allowed_extensions

    @staticmethod
    def is_allowed_content_type(content_type: str | None) -> bool:
        if not content_type:
            return False

        return content_type.lower() in settings.allowed_content_types

    @classmethod
    def validate_image_file(cls, file: UploadFile) -> None:
        if not cls.is_allowed_image_extension(file.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file extension. Use .jpg, .jpeg or .png.",
            )

        if not cls.is_allowed_content_type(file.content_type):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid content type. Use image/jpeg or image/png.",
            )

    @staticmethod
    async def read_upload_file(file: UploadFile) -> bytes:
        chunks: list[bytes] = []
        total_size = 0
        max_upload_size_bytes = settings.max_upload_size_mb * 1024 * 1024

        while chunk := await file.read(UPLOAD_READ_CHUNK_SIZE):
            total_size += len(chunk)

            if total_size > max_upload_size_bytes:
                raise HTTPException(
                    status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                    detail=(
                        "Uploaded file is too large. "
                        f"Maximum allowed size is {settings.max_upload_size_mb} MB."
                    ),
                )

            chunks.append(chunk)

        image_bytes = b"".join(chunks)

        if not image_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty.",
            )

        return image_bytes

    @staticmethod
    def validate_image_dimensions(image: np.ndarray) -> None:
        height, width = image.shape[:2]
        total_pixels = width * height

        if (
            width > settings.max_image_width
            or height > settings.max_image_height
            or total_pixels > settings.max_image_pixels
        ):
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail=(
                    "Image resolution is too large. "
                    f"Maximum allowed resolution is {settings.max_image_width}x"
                    f"{settings.max_image_height} and {settings.max_image_pixels} pixels."
                ),
            )

    @staticmethod
    def bytes_to_cv2_image(image_bytes: bytes) -> np.ndarray:
        image_array = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        if image is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is not a valid image.",
            )

        ImageService.validate_image_dimensions(image)

        return image

    @staticmethod
    def save_annotated_image(image: np.ndarray, original_filename: str | None) -> str:
        settings.outputs_dir.mkdir(parents=True, exist_ok=True)

        original_path = Path(original_filename or "image.jpg")
        safe_stem = "".join(
            char if char.isalnum() or char in {"-", "_"} else "_"
            for char in original_path.stem
        )
        extension = original_path.suffix.lower()

        if extension not in settings.allowed_extensions:
            extension = ".jpg"

        output_filename = f"{safe_stem}_{uuid4().hex[:8]}{extension}"
        output_path = settings.outputs_dir / output_filename

        success = cv2.imwrite(str(output_path), image)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not save annotated image.",
            )

        return output_path.as_posix()
