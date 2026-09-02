"""Investigation report routes for FraudGraph API."""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from backend.api.data_service import DataService

router = APIRouter(tags=["Investigation"])


def get_data_service() -> DataService:
    return DataService.get_instance()


@router.get("/investigation/{entity_type}/{entity_id}", summary="Phase 4 Forensic Investigation Report")
def get_investigation_report(
    entity_type: str,
    entity_id: str,
    service: DataService = Depends(get_data_service),
) -> Dict[str, Any]:
    """Retrieves structured Phase 4 investigation report JSON for Customer, Transaction, or Fraud Ring."""
    valid_types = {"customer", "cust", "transaction", "txn", "ring", "fraud_ring", "fraud-ring", "fr"}
    if entity_type.lower() not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid entity type '{entity_type}'. Must be one of: customer, transaction, ring.",
        )

    report = service.get_investigation_report(entity_type, entity_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation report for {entity_type} '{entity_id}' not found.",
        )
    return report
