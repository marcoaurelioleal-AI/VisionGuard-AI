from collections import defaultdict, deque
from threading import Lock
from time import monotonic

from fastapi import Request, status
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import JSONResponse, Response

from app.core.config import settings

HEAVY_ENDPOINT_PATHS = {
    "/detect/faces",
    "/detect/faces/annotated",
    "/detect/objects",
    "/detect/objects/annotated",
    "/detect/all",
    "/detect/all/annotated",
    "/analyze/image",
}


class InMemoryRateLimiter:
    """Simple fixed-window limiter for a single-process MVP deployment."""

    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str) -> tuple[bool, int]:
        now = monotonic()
        window_start = now - self.window_seconds

        with self._lock:
            request_times = self._requests[key]

            while request_times and request_times[0] <= window_start:
                request_times.popleft()

            if len(request_times) >= self.max_requests:
                retry_after = max(1, int(self.window_seconds - (now - request_times[0])))
                return False, retry_after

            request_times.append(now)
            return True, 0

    def reset(self) -> None:
        with self._lock:
            self._requests.clear()


rate_limiter = InMemoryRateLimiter(
    max_requests=settings.rate_limit_max_requests,
    window_seconds=settings.rate_limit_window_seconds,
)


def get_client_identifier(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    if request.client is None:
        return "unknown-client"

    return request.client.host


async def rate_limit_heavy_endpoints(
    request: Request,
    call_next: RequestResponseEndpoint,
) -> Response:
    if request.method == "POST" and request.url.path in HEAVY_ENDPOINT_PATHS:
        client_id = get_client_identifier(request)
        rate_limit_key = f"{client_id}:{request.url.path}"
        is_allowed, retry_after = rate_limiter.check(rate_limit_key)

        if not is_allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": (
                        "Too many requests. Please wait before sending another "
                        "image analysis request."
                    )
                },
                headers={"Retry-After": str(retry_after)},
            )

    return await call_next(request)
