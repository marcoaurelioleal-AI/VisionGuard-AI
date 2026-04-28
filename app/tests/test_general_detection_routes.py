from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_combined_detection_route_exists() -> None:
    response = client.post(
        "/detect/all",
        files={"file": ("image.jpg", b"fake-image-content", "image/jpeg")},
    )

    assert response.status_code == 400


def test_combined_detection_rejects_invalid_confidence_threshold() -> None:
    response = client.post(
        "/detect/all?confidence_threshold=1.5",
        files={"file": ("image.jpg", b"fake-image-content", "image/jpeg")},
    )

    assert response.status_code == 422


def test_combined_detection_rejects_invalid_face_parameters() -> None:
    response = client.post(
        "/detect/all?scale_factor=1.0&min_neighbors=0&min_size=19",
        files={"file": ("image.jpg", b"fake-image-content", "image/jpeg")},
    )

    assert response.status_code == 422


def test_annotated_combined_detection_route_exists() -> None:
    response = client.post(
        "/detect/all/annotated",
        files={"file": ("image.jpg", b"fake-image-content", "image/jpeg")},
    )

    assert response.status_code == 400
