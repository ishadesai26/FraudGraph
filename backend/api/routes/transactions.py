"""Transaction investigation routes for FraudGraph API."""

from fastapi import APIRouter, Depends, HTTPException, status
from backend.api.schemas import TransactionDetailResponse
from backend.api.data_service import DataService

router = APIRouter(tags=["Transactions"])


def get_data_service() -> DataService:
    return DataService.get_instance()


@router.get("/transactions/{transaction_id}", response_model=TransactionDetailResponse, summary="Transaction Forensic Inspection")
def get_transaction(
    transaction_id: str,
    service: DataService = Depends(get_data_service),
) -> TransactionDetailResponse:
    """Retrieves transaction forensic details, customer link, and network context."""
    detail = service.get_transaction_detail(transaction_id)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction '{transaction_id}' not found.",
        )
    return detail
