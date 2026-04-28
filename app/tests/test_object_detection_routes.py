from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_object_detection_rejects_invalid_confidence_threshold() -> None:
    response = client.post(
        "/detect/objects?confidence_threshold=1.5",
        files={"file": ("image.jpg", b"fake-image-content", "image/jpeg")},
    )

    assert response.status_code == 422
