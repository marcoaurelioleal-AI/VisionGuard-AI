import asyncio

import numpy as np
import pytest
from fastapi import HTTPException, status

from app.core.config import settings
from app.services.image_service import ImageService


class FakeUploadFile:
    def __init__(self, chunks: list[bytes]) -> None:
        self.chunks = chunks

    async def read(self, size: int = -1) -> bytes:
        if not self.chunks:
            return b""

        return self.chunks.pop(0)


def test_allowed_image_extensions() -> None:
    assert ImageService.is_allowed_image_extension("photo.jpg")
    assert ImageService.is_allowed_image_extension("photo.jpeg")
    assert ImageService.is_allowed_image_extension("photo.png")


def test_rejects_invalid_image_extension() -> None:
    assert not ImageService.is_allowed_image_extension("document.pdf")
    assert not ImageService.is_allowed_image_extension("script.py")
    assert not ImageService.is_allowed_image_extension(None)


def test_read_upload_file_rejects_files_above_max_size(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "max_upload_size_mb", 1)
    fake_file = FakeUploadFile([b"a" * (1024 * 1024), b"b"])

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(ImageService.read_upload_file(fake_file))

    assert exc_info.value.status_code == status.HTTP_413_CONTENT_TOO_LARGE


def test_validate_image_dimensions_rejects_large_resolution(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "max_image_width", 100)
    monkeypatch.setattr(settings, "max_image_height", 100)
    monkeypatch.setattr(settings, "max_image_pixels", 10_000)
    image = np.zeros((101, 100, 3), dtype=np.uint8)

    with pytest.raises(HTTPException) as exc_info:
        ImageService.validate_image_dimensions(image)

    assert exc_info.value.status_code == status.HTTP_413_CONTENT_TOO_LARGE


def test_validate_image_dimensions_accepts_image_within_limits(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "max_image_width", 100)
    monkeypatch.setattr(settings, "max_image_height", 100)
    monkeypatch.setattr(settings, "max_image_pixels", 10_000)
    image = np.zeros((100, 100, 3), dtype=np.uint8)

    ImageService.validate_image_dimensions(image)
