"""Health route for FraudGraph API."""

from fastapi import APIRouter
from backend.api.schemas import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse, summary="API Health Check")
def get_health() -> HealthResponse:
    """Returns service operational status."""
    return HealthResponse(status="ok", service="FraudGraph", version="1.0.0")
