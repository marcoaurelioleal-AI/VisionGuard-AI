from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_face_detection_rejects_invalid_scale_factor() -> None:
    response = client.post(
        "/detect/faces?scale_factor=1.0",
        files={"file": ("image.jpg", b"fake-image-content", "image/jpeg")},
    )

    assert response.status_code == 422


def test_face_detection_rejects_invalid_min_neighbors() -> None:
    response = client.post(
        "/detect/faces?min_neighbors=0",
        files={"file": ("image.jpg", b"fake-image-content", "image/jpeg")},
    )

    assert response.status_code == 422


def test_face_detection_rejects_invalid_min_size() -> None:
    response = client.post(
        "/detect/faces?min_size=19",
        files={"file": ("image.jpg", b"fake-image-content", "image/jpeg")},
    )

    assert response.status_code == 422


def test_annotated_face_detection_route_exists() -> None:
    response = client.post(
        "/detect/faces/annotated",
        files={"file": ("image.jpg", b"fake-image-content", "image/jpeg")},
    )

    assert response.status_code == 400


def test_annotated_face_detection_rejects_invalid_query_parameters() -> None:
    response = client.post(
        "/detect/faces/annotated?scale_factor=1.0&min_neighbors=0&min_size=19",
        files={"file": ("image.jpg", b"fake-image-content", "image/jpeg")},
    )

    assert response.status_code == 422
