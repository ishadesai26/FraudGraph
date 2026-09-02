"""Unit and Integration tests for FraudGraph Phase 6 Real-Time Simulation."""

import pytest
from fastapi.testclient import TestClient
from backend.api.main import app
from backend.simulation.scenarios import SCENARIOS, get_scenario_by_id
from backend.simulation.transaction_generator import TransactionGenerator
from backend.simulation.risk_simulator import RiskSimulator
from backend.agents.schemas import SimulationResponse


@pytest.fixture(scope="module")
def client():
    """FastAPI TestClient fixture."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="module")
def simulator():
    """RiskSimulator instance fixture."""
    return RiskSimulator()


def test_simulation_scenarios_definitions():
    """Verify all 6 demo scenarios are correctly defined."""
    assert len(SCENARIOS) == 6
    scenario_ids = [s.scenario_id for s in SCENARIOS]
    expected_ids = [
        "NORMAL_TXN",
        "HIGH_VALUE_SPIKE",
        "SHARED_DEVICE_CLUSTER",
        "SHARED_IP_PROXY",
        "SYNCHRONIZED_BURST",
        "FRAUD_RING_SYNDICATE",
    ]
    for exp in expected_ids:
        assert exp in scenario_ids

    sc = get_scenario_by_id("FRAUD_RING_SYNDICATE")
    assert sc.scenario_id == "FRAUD_RING_SYNDICATE"
    assert "amount" in sc.sample_payload
    assert "customer_id" in sc.sample_payload


def test_transaction_generator_generation():
    """Verify TransactionGenerator produces valid, foreign-key compatible transaction payloads."""
    txn = TransactionGenerator.generate("HIGH_VALUE_SPIKE")
    assert "transaction_id" in txn
    assert txn["transaction_id"].startswith("SIM_")
    assert "timestamp" in txn
    assert txn["amount"] == 78500.0
    assert txn["scenario_id"] == "HIGH_VALUE_SPIKE"


def test_live_risk_simulator_normal_scenario(simulator):
    """Verify simulation of a normal retail transaction produces LOW_RISK decision."""
    txn = TransactionGenerator.generate("NORMAL_TXN")
    response = simulator.simulate_and_investigate(txn, scenario_id="NORMAL_TXN")

    assert isinstance(response, SimulationResponse)
    assert response.risk["composite_risk_score"] < 45.0
    assert response.decision.status in ["LOW_RISK", "REVIEW"]
    assert len(response.agent_trace) == 6


def test_live_risk_simulator_fraud_ring_scenario(simulator):
    """Verify simulation of a syndicate transaction produces HIGH_RISK disposition and agent consensus."""
    txn = TransactionGenerator.generate("FRAUD_RING_SYNDICATE")
    response = simulator.simulate_and_investigate(txn, scenario_id="FRAUD_RING_SYNDICATE")

    assert isinstance(response, SimulationResponse)
    assert response.risk["composite_risk_score"] >= 70.0
    assert response.decision.status in ["HIGH_RISK", "ENHANCED_REVIEW"]
    assert any(e["signal"] in ["syndicate_ring_membership", "supervised_ml_high_confidence_fraud"] for e in response.evidence["evidence_items"])


def test_api_simulation_scenarios_endpoint(client):
    """Test GET /api/simulation/scenarios."""
    response = client.get("/api/simulation/scenarios")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 6
    assert data[0]["scenario_id"] == "NORMAL_TXN"


def test_api_simulation_analyze_endpoint(client):
    """Test POST /api/simulation/analyze endpoint."""
    txn_payload = {
        "customer_id": "CUST_00028",
        "amount": 45000.0,
        "merchant_id": "MERCH_0067",
        "payment_type": "UPI",
        "device_id": "DEV_00028",
        "ip_id": "IP_00028",
        "city": "Mumbai",
        "seconds_since_previous": 25,
    }

    response = client.post(
        "/api/simulation/analyze",
        json={"scenario_id": "FRAUD_RING_SYNDICATE", "transaction": txn_payload},
    )
    assert response.status_code == 200
    data = response.json()
    assert "simulation_id" in data
    assert "risk" in data
    assert "decision" in data
    assert len(data["agent_trace"]) == 6
    assert data["decision"]["status"] in ["HIGH_RISK", "ENHANCED_REVIEW"]
