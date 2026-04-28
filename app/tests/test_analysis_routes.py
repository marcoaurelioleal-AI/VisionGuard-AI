from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_analysis_history_route_exists() -> None:
    response = client.get("/analysis/history")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_analysis_history_rejects_invalid_limit() -> None:
    response = client.get("/analysis/history?limit=0")

    assert response.status_code == 422


def test_analyze_image_rejects_invalid_query_parameters() -> None:
    response = client.post(
        "/analyze/image?confidence_threshold=1.5&scale_factor=1.0",
        files={"file": ("image.jpg", b"fake-image-content", "image/jpeg")},
    )

    assert response.status_code == 422
