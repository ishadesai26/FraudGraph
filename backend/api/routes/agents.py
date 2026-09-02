"""FastAPI routes for Multi-Agent Fraud Investigation."""

from fastapi import APIRouter, HTTPException, Path
from backend.agents.schemas import AgentInvestigationRequest, AgentInvestigationResult
from backend.agents.orchestrator import AgentOrchestrator
from backend.api.data_service import DataService

router = APIRouter(prefix="/api/agents", tags=["Multi-Agent Investigation"])
orchestrator = AgentOrchestrator()


@router.post("/investigate", response_model=AgentInvestigationResult)
def trigger_agent_investigation(request: AgentInvestigationRequest):
    """Triggers the 6-agent collaborative fraud investigation on an entity."""
    entity_type = request.entity_type.lower()
    entity_id = request.entity_id.strip().upper()

    if entity_type not in ["customer", "transaction", "ring"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid entity_type '{entity_type}'. Must be 'customer', 'transaction', or 'ring'.",
        )

    data_service = DataService.get_instance()

    # Load context according to entity type
    if entity_type == "customer":
        cust_detail_raw = data_service.get_customer_detail(entity_id)
        if not cust_detail_raw:
            raise HTTPException(status_code=404, detail=f"Customer '{entity_id}' not found.")
        cust_detail = cust_detail_raw.model_dump() if hasattr(cust_detail_raw, "model_dump") else cust_detail_raw

        # Extract ML risk data
        signals = {s["name"]: s["value"] for s in cust_detail.get("contributing_signals", [])}
        risk_data = {
            "risk_score": cust_detail.get("risk_score", 0.0),
            "supervised_model_probability": signals.get("supervised_model_probability", 0.0) / 100.0,
            "unsupervised_anomaly_score": signals.get("unsupervised_anomaly_score", 0.0),
            "baseline_probability": (signals.get("supervised_model_probability", 0.0) / 100.0) * 0.8,
            "graph_model_probability": signals.get("supervised_model_probability", 0.0) / 100.0,
        }

        graph_data = {
            "network_risk_score": signals.get("network_risk_score", 0.0),
            "associated_ring_id": cust_detail.get("associated_ring_id"),
            "member_role": cust_detail.get("member_role", "MEMBER"),
            "shared_devices": cust_detail.get("shared_devices", []),
            "shared_payments": cust_detail.get("shared_payments", []),
            "shared_ips": [],
            "connected_neighbors": cust_detail.get("connected_neighbors", []),
        }

        behavior_data = {
            "total_transactions": cust_detail.get("total_transactions", 0),
            "total_spend": cust_detail.get("total_spend", 0.0),
            "account_age_days": cust_detail.get("account_age_days", 90),
            "kyc_verified": cust_detail.get("kyc_verified", True),
        }

        timeline = cust_detail.get("timeline", [])

    elif entity_type == "ring":
        ring_detail_raw = data_service.get_fraud_ring_detail(entity_id)
        if not ring_detail_raw:
            raise HTTPException(status_code=404, detail=f"Fraud Ring '{entity_id}' not found.")
        ring_detail = ring_detail_raw.model_dump() if hasattr(ring_detail_raw, "model_dump") else ring_detail_raw

        risk_data = {
            "risk_score": ring_detail.get("risk_score", 100.0),
            "supervised_model_probability": 0.95,
            "unsupervised_anomaly_score": 90.0,
        }
        graph_data = {
            "network_risk_score": 100.0,
            "associated_ring_id": entity_id,
            "member_role": "SYNDICATE_COMMUNITY",
            "shared_devices": [{"resource_id": f"DEV_{i}", "shared_with_count": 4} for i in range(ring_detail.get("shared_devices_count", 0))],
            "shared_payments": [{"resource_id": f"PM_{i}", "shared_with_count": 3} for i in range(ring_detail.get("shared_payments_count", 0))],
        }
        behavior_data = {
            "total_transactions": ring_detail.get("transaction_count", 0),
            "total_spend": ring_detail.get("transaction_volume", 0.0),
        }
        timeline = []

    else:  # transaction
        txn_detail_raw = data_service.get_transaction_detail(entity_id)
        if not txn_detail_raw:
            raise HTTPException(status_code=404, detail=f"Transaction '{entity_id}' not found.")
        txn_detail = txn_detail_raw.model_dump() if hasattr(txn_detail_raw, "model_dump") else txn_detail_raw

        risk_data = {
            "risk_score": txn_detail.get("risk_score", 0.0),
            "supervised_model_probability": txn_detail.get("risk_score", 0.0) / 100.0,
            "unsupervised_anomaly_score": 40.0,
        }
        graph_data = {"network_risk_score": txn_detail.get("risk_score", 0.0)}
        behavior_data = {"total_transactions": 1, "total_spend": txn_detail.get("amount", 0.0)}
        timeline = [{
            "transaction_id": entity_id,
            "timestamp": txn_detail.get("timestamp", ""),
            "amount": txn_detail.get("amount", 0.0),
            "merchant_id": txn_detail.get("merchant_id", ""),
            "payment_type": txn_detail.get("payment_type", ""),
            "device_id": txn_detail.get("device_id", ""),
            "ip_id": txn_detail.get("ip_id", ""),
            "city": txn_detail.get("city", ""),
            "is_burst": False,
        }]

    result = orchestrator.investigate(
        entity_type=entity_type,
        entity_id=entity_id,
        risk_data=risk_data,
        graph_data=graph_data,
        behavior_data=behavior_data,
        timeline=timeline,
    )
    return result


@router.get("/investigation/{investigation_id}", response_model=AgentInvestigationResult)
def get_saved_investigation(investigation_id: str = Path(..., description="Investigation ID, e.g. INV_CUSTOMER_CUST_00028")):
    """Retrieves a previously saved multi-agent investigation JSON artifact."""
    result = orchestrator.load_investigation(investigation_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Investigation '{investigation_id}' not found.")
    return result
