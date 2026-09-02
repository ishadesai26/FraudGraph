"""Customer investigation routes for FraudGraph API."""

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from backend.api.schemas import CustomerSummary, CustomerDetailResponse, PaginatedResponse
from backend.api.data_service import DataService

router = APIRouter(tags=["Customers"])


def get_data_service() -> DataService:
    return DataService.get_instance()


@router.get("/customers", response_model=PaginatedResponse[CustomerSummary], summary="Paginated Customer Explorer")
def list_customers(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(25, ge=1, le=100, description="Items per page (max 100)"),
    risk_level: Optional[str] = Query(None, description="Filter by risk tier (LOW, MEDIUM, HIGH, CRITICAL)"),
    ring_id: Optional[str] = Query(None, description="Filter by associated fraud ring ID (e.g. FR_017)"),
    minimum_risk_score: Optional[float] = Query(None, ge=0.0, le=100.0, description="Filter by minimum composite risk score"),
    search: Optional[str] = Query(None, description="Fuzzy search across customer ID, ring ID, and signals"),
    service: DataService = Depends(get_data_service),
) -> PaginatedResponse[CustomerSummary]:
    """Retrieves a searchable, filterable, paginated list of customers."""
    items, total, total_pages = service.get_customers(
        page=page,
        page_size=page_size,
        risk_level=risk_level,
        ring_id=ring_id,
        min_risk_score=minimum_risk_score,
        search=search,
    )
    return PaginatedResponse[CustomerSummary](
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )


@router.get("/customers/{customer_id}", response_model=CustomerDetailResponse, summary="Customer Forensic Dossier")
def get_customer(
    customer_id: str,
    service: DataService = Depends(get_data_service),
) -> CustomerDetailResponse:
    """Retrieves full forensic investigation profile, model evidence, graph links, and action plan."""
    detail = service.get_customer_detail(customer_id)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer '{customer_id}' not found in registry.",
        )
    return detail
