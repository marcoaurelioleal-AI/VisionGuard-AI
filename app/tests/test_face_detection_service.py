import numpy as np

from app.services.face_detection_service import FaceDetectionService


class FakeCascade:
    def __init__(self) -> None:
        self.received_scale_factor: float | None = None
        self.received_min_neighbors: int | None = None
        self.received_min_size: tuple[int, int] | None = None

    def detectMultiScale(
        self,
        image: np.ndarray,
        scaleFactor: float,
        minNeighbors: int,
        minSize: tuple[int, int],
    ) -> list[tuple[int, int, int, int]]:
        self.received_scale_factor = scaleFactor
        self.received_min_neighbors = minNeighbors
        self.received_min_size = minSize

        return [(10, 20, 100, 120)]


def test_face_detection_passes_query_parameters_to_haar_cascade() -> None:
    service = FaceDetectionService()
    fake_cascade = FakeCascade()
    service.face_cascade = fake_cascade
    image = np.zeros((200, 200, 3), dtype=np.uint8)

    faces = service.detect_faces(
        image,
        scale_factor=1.2,
        min_neighbors=6,
        min_size=40,
    )

    assert fake_cascade.received_scale_factor == 1.2
    assert fake_cascade.received_min_neighbors == 6
    assert fake_cascade.received_min_size == (40, 40)
    assert faces[0].x == 10
    assert faces[0].y == 20
    assert faces[0].width == 100
    assert faces[0].height == 120
