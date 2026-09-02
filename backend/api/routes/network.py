"""Network subgraph visualization routes for FraudGraph API."""

from fastapi import APIRouter, Depends, HTTPException, status
from backend.api.schemas import NetworkGraphResponse
from backend.api.data_service import DataService

router = APIRouter(tags=["Network"])


def get_data_service() -> DataService:
    return DataService.get_instance()


@router.get("/network/{entity_type}/{entity_id}", response_model=NetworkGraphResponse, summary="Cytoscape Network Neighborhood")
def get_network_graph(
    entity_type: str,
    entity_id: str,
    service: DataService = Depends(get_data_service),
) -> NetworkGraphResponse:
    """Extracts localized, interactive graph neighborhood (1-2 hops) formatted for Cytoscape.js."""
    valid_types = {"customer", "cust", "transaction", "txn", "ring", "fraud_ring", "fraud-ring", "fr"}
    if entity_type.lower() not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid entity type '{entity_type}'. Must be one of: customer, transaction, ring.",
        )

    graph_res = service.get_network_subgraph(entity_type, entity_id)
    if not graph_res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Network data for {entity_type} '{entity_id}' not found.",
        )
    return graph_res
