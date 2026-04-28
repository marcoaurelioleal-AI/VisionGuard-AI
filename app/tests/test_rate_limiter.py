from fastapi.testclient import TestClient

from app.core.rate_limiter import rate_limiter
from app.main import app


client = TestClient(app)


def test_heavy_detection_endpoint_returns_429_when_rate_limit_is_exceeded() -> None:
    original_max_requests = rate_limiter.max_requests
    original_window_seconds = rate_limiter.window_seconds

    try:
        rate_limiter.reset()
        rate_limiter.max_requests = 1
        rate_limiter.window_seconds = 60

        first_response = client.post("/detect/faces")
        second_response = client.post("/detect/faces")

        assert first_response.status_code == 422
        assert second_response.status_code == 429
        assert second_response.json()["detail"].startswith("Too many requests")
        assert "Retry-After" in second_response.headers
    finally:
        rate_limiter.max_requests = original_max_requests
        rate_limiter.window_seconds = original_window_seconds
        rate_limiter.reset()


def test_lightweight_health_endpoint_is_not_rate_limited() -> None:
    original_max_requests = rate_limiter.max_requests

    try:
        rate_limiter.reset()
        rate_limiter.max_requests = 1

        first_response = client.get("/health")
        second_response = client.get("/health")

        assert first_response.status_code == 200
        assert second_response.status_code == 200
    finally:
        rate_limiter.max_requests = original_max_requests
        rate_limiter.reset()
