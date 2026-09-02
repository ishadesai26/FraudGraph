"""Dashboard routes for FraudGraph API."""

from fastapi import APIRouter, Depends
from backend.api.schemas import DashboardStatsResponse
from backend.api.data_service import DataService

router = APIRouter(tags=["Dashboard"])


def get_data_service() -> DataService:
    return DataService.get_instance()


@router.get("/dashboard", response_model=DashboardStatsResponse, summary="Dashboard KPI Statistics")
def get_dashboard_metrics(service: DataService = Depends(get_data_service)) -> DashboardStatsResponse:
    """Returns high-level platform statistics, risk distribution, and key flagged entities."""
    return service.get_dashboard_stats()
