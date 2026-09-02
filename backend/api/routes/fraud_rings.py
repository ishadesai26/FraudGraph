"""Fraud ring syndicate investigation routes for FraudGraph API."""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from backend.api.schemas import FraudRingSummary, FraudRingDetailResponse, PaginatedResponse
from backend.api.data_service import DataService

router = APIRouter(tags=["Fraud Rings"])


def get_data_service() -> DataService:
    return DataService.get_instance()


@router.get("/fraud-rings", response_model=PaginatedResponse[FraudRingSummary], summary="Detected Fraud Rings Directory")
def list_fraud_rings(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(25, ge=1, le=100, description="Items per page"),
    service: DataService = Depends(get_data_service),
) -> PaginatedResponse[FraudRingSummary]:
    """Retrieves paginated list of all detected fraud rings and syndicates."""
    items, total, total_pages = service.get_fraud_rings(page=page, page_size=page_size)
    return PaginatedResponse[FraudRingSummary](
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )


@router.get("/fraud-rings/{ring_id}", response_model=FraudRingDetailResponse, summary="Syndicate Forensic Dossier")
def get_fraud_ring(
    ring_id: str,
    service: DataService = Depends(get_data_service),
) -> FraudRingDetailResponse:
    """Retrieves full syndicate profile, member roster, shared infrastructure, and disruption actions."""
    detail = service.get_fraud_ring_detail(ring_id)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fraud ring '{ring_id}' not found.",
        )
    return detail
