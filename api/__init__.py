"""LangExtract API module."""

__version__ = "1.0.0"
__author__ = "LangExtract API Team"
__description__ = "FastAPI-based REST API for LangExtract framework"

from api.main import app
from api.config import get_settings
from api.models import (
    ExtractionRequest,
    ExtractionResponse,
    ExtractionStatus,
    HealthResponse,
    AuthRequest,
    AuthResponse,
    ModelInfo
)

__all__ = [
    "app",
    "get_settings",
    "ExtractionRequest",
    "ExtractionResponse",
    "ExtractionStatus",
    "HealthResponse",
    "AuthRequest",
    "AuthResponse",
    "ModelInfo"
]