from pathlib import Path

from pydantic import BaseModel

DEFAULT_CONFIDENCE_THRESHOLD = 0.40
DEFAULT_FACE_SCALE_FACTOR = 1.1
DEFAULT_FACE_MIN_NEIGHBORS = 5
DEFAULT_FACE_MIN_SIZE = 30
YOLO_MODEL_NAME = "yolo11n.pt"
MAX_UPLOAD_SIZE_MB = 10
MAX_IMAGE_WIDTH = 4096
MAX_IMAGE_HEIGHT = 4096
MAX_IMAGE_PIXELS = 16_000_000
RATE_LIMIT_MAX_REQUESTS = 60
RATE_LIMIT_WINDOW_SECONDS = 60


class Settings(BaseModel):
    """Central project settings used by services and routes."""

    app_name: str = "VisionGuard API"
    allowed_extensions: set[str] = {".jpg", ".jpeg", ".png"}
    allowed_content_types: set[str] = {"image/jpeg", "image/png"}
    outputs_dir: Path = Path("outputs")
    data_dir: Path = Path("data")
    database_path: Path = Path("data/visionguard.db")
    yolo_model_name: str = YOLO_MODEL_NAME
    max_upload_size_mb: int = MAX_UPLOAD_SIZE_MB
    max_image_width: int = MAX_IMAGE_WIDTH
    max_image_height: int = MAX_IMAGE_HEIGHT
    max_image_pixels: int = MAX_IMAGE_PIXELS
    default_confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD
    default_face_scale_factor: float = DEFAULT_FACE_SCALE_FACTOR
    default_face_min_neighbors: int = DEFAULT_FACE_MIN_NEIGHBORS
    default_face_min_size: int = DEFAULT_FACE_MIN_SIZE
    rate_limit_max_requests: int = RATE_LIMIT_MAX_REQUESTS
    rate_limit_window_seconds: int = RATE_LIMIT_WINDOW_SECONDS


settings = Settings()
