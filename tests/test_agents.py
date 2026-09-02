"""Unit and Integration tests for FraudGraph Phase 6 Multi-Agent Architecture."""

import pytest
from fastapi.testclient import TestClient
from backend.api.main import app
from backend.agents.orchestrator import AgentOrchestrator
from backend.agents.risk_agent import RiskAgent
from backend.agents.graph_agent import GraphAgent
from backend.agents.behavior_agent import BehaviorAgent
from backend.agents.evidence_agent import EvidenceAgent
from backend.agents.investigator_agent import InvestigatorAgent
from backend.agents.decision_agent import DecisionAgent
from backend.agents.schemas import AgentInvestigationResult


@pytest.fixture(scope="module")
def client():
    """FastAPI TestClient fixture."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="module")
def orchestrator():
    """AgentOrchestrator instance fixture."""
    return AgentOrchestrator()


def test_individual_agents_execution():
    """Verify each specialized agent executes independently and produces standard trace output."""
    context = {
        "entity_type": "customer",
        "entity_id": "CUST_00028",
        "risk_data": {
            "risk_score": 95.0,
            "supervised_model_probability": 0.98,
            "unsupervised_anomaly_score": 90.0,
        },
        "graph_data": {
            "network_risk_score": 95.0,
            "associated_ring_id": "FR_015",
            "member_role": "CORE",
            "shared_devices": [{"resource_id": "DEV_0001", "shared_with_count": 5}],
            "shared_payments": [{"resource_id": "PM_0001", "shared_with_count": 4}],
        },
        "behavior_data": {
            "total_transactions": 15,
            "total_spend": 500000.0,
            "account_age_days": 180,
            "kyc_verified": True,
        },
        "timeline": [
            {"amount": 50000.0, "is_burst": True, "seconds_since_previous": 20},
            {"amount": 45000.0, "is_burst": True, "seconds_since_previous": 30},
        ],
    }

    # 1. RiskAgent
    risk_agent = RiskAgent()
    risk_res = risk_agent.run(context)
    assert risk_res["trace_step"].status == "completed"
    assert risk_res["trace_step"].signals_found >= 2
    assert risk_res["ml_risk_level"] in ["HIGH", "CRITICAL"]

    # 2. GraphAgent
    graph_agent = GraphAgent()
    graph_res = graph_agent.run(context)
    assert graph_res["trace_step"].status == "completed"
    assert graph_res["trace_step"].signals_found >= 2
    assert graph_res["network_risk_level"] in ["HIGH", "CRITICAL"]

    # 3. BehaviorAgent
    behavior_agent = BehaviorAgent()
    beh_res = behavior_agent.run(context)
    assert beh_res["trace_step"].status == "completed"
    assert beh_res["trace_step"].signals_found >= 1
    assert beh_res["burst_count"] == 2

    # 4. EvidenceAgent
    evidence_agent = EvidenceAgent()
    context["risk_agent_output"] = risk_res
    context["graph_agent_output"] = graph_res
    context["behavior_agent_output"] = beh_res
    ev_res = evidence_agent.run(context)
    assert ev_res["trace_step"].status == "completed"
    assert len(ev_res["evidence"]) >= 3
    assert ev_res["evidence_coverage"] >= 75.0

    # 5. InvestigatorAgent
    inv_agent = InvestigatorAgent()
    context["evidence_agent_output"] = ev_res
    inv_res = inv_agent.run(context)
    assert inv_res["trace_step"].status == "completed"
    assert len(inv_res["key_findings"]) >= 1
    assert len(inv_res["entities_to_review"]) >= 2

    # 6. DecisionAgent
    dec_agent = DecisionAgent()
    context["investigator_agent_output"] = inv_res
    dec_res = dec_agent.run(context)
    assert dec_res["trace_step"].status == "completed"
    assert dec_res["decision"].status in ["HIGH_RISK", "ENHANCED_REVIEW"]
    assert dec_res["decision"].confidence in ["HIGH", "MEDIUM"]


def test_orchestrator_investigation_flow(orchestrator):
    """Test full multi-agent orchestration on a known high-risk customer."""
    result = orchestrator.investigate(
        entity_type="customer",
        entity_id="CUST_00028",
        risk_data={"risk_score": 99.1, "supervised_model_probability": 0.998, "unsupervised_anomaly_score": 100.0},
        graph_data={"network_risk_score": 96.95, "associated_ring_id": "FR_015", "member_role": "MEMBER"},
        behavior_data={"total_transactions": 15, "total_spend": 488216.93},
    )

    assert isinstance(result, AgentInvestigationResult)
    assert result.entity_id == "CUST_00028"
    assert result.decision.status == "HIGH_RISK"
    assert len(result.agent_trace) == 6
    assert all(step.status == "completed" for step in result.agent_trace)
    assert len(result.key_findings) > 0
    assert result.evidence_graph is not None
    assert len(result.evidence_graph.nodes) >= 3


def test_evidence_provenance_strictness(orchestrator):
    """Verify that every single evidence item has a valid, known source agent."""
    result = orchestrator.investigate(
        entity_type="customer",
        entity_id="CUST_00028",
        risk_data={"risk_score": 85.0, "supervised_model_probability": 0.88},
        graph_data={"network_risk_score": 80.0, "associated_ring_id": "FR_015"},
    )

    valid_agents = {"RiskAgent", "GraphAgent", "BehaviorAgent", "EvidenceAgent", "InvestigatorAgent", "DecisionAgent"}
    for item in result.evidence_items:
        assert item.source_agent in valid_agents
        assert len(item.signal) > 0
        assert item.severity in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


def test_conflict_detection_mechanism(orchestrator):
    """Verify conflict detection when model indicates high risk but network topology is clean."""
    result = orchestrator.investigate(
        entity_type="customer",
        entity_id="CUST_CONFLICT_TEST",
        risk_data={"risk_score": 90.0, "supervised_model_probability": 0.95, "unsupervised_anomaly_score": 85.0},
        graph_data={"network_risk_score": 10.0, "associated_ring_id": None, "shared_devices": [], "shared_payments": []},
        behavior_data={"total_transactions": 5, "total_spend": 2000.0},
    )

    assert len(result.conflicts) >= 1
    assert any(c.type == "model_network_discrepancy" for c in result.conflicts)


def test_evidence_coverage_vs_fraud_prob_distinction(orchestrator):
    """Verify evidence coverage measures data completeness (0-100), not fraud probability."""
    # Low risk entity with complete data -> High Coverage, Low Risk Score
    result = orchestrator.investigate(
        entity_type="customer",
        entity_id="CUST_00803",
        risk_data={"risk_score": 12.0, "supervised_model_probability": 0.05, "unsupervised_anomaly_score": 10.0},
        graph_data={"network_risk_score": 5.0, "shared_devices": [], "shared_payments": []},
        behavior_data={"total_transactions": 10, "total_spend": 12000.0, "account_age_days": 200, "kyc_verified": True},
    )

    assert result.decision.risk_score < 30.0
    assert result.decision.status == "LOW_RISK"
    assert result.decision.evidence_coverage >= 75.0  # High data completeness!


def test_investigation_persistence_and_retrieval(orchestrator):
    """Verify completed investigations are saved as JSON artifacts and can be reloaded."""
    result = orchestrator.investigate(
        entity_type="customer",
        entity_id="CUST_PERSIST_TEST",
        risk_data={"risk_score": 88.0},
    )

    loaded = orchestrator.load_investigation(result.investigation_id)
    assert loaded is not None
    assert loaded.investigation_id == result.investigation_id
    assert loaded.risk_score == result.risk_score
    assert loaded.decision.status == result.decision.status


def test_api_agents_investigate_endpoint(client):
    """Test POST /api/agents/investigate via FastAPI client."""
    response = client.post(
        "/api/agents/investigate",
        json={"entity_type": "customer", "entity_id": "CUST_00028"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["entity_id"] == "CUST_00028"
    assert data["decision"]["status"] in ["HIGH_RISK", "ENHANCED_REVIEW"]
    assert len(data["agent_trace"]) == 6

    # Test GET saved investigation
    inv_id = data["investigation_id"]
    get_res = client.get(f"/api/agents/investigation/{inv_id}")
    assert get_res.status_code == 200
    assert get_res.json()["investigation_id"] == inv_id


def test_api_agents_investigate_404_and_400(client):
    """Test error handling on invalid entity types and nonexistent IDs."""
    # 400 Bad Request on invalid entity type
    res_400 = client.post(
        "/api/agents/investigate",
        json={"entity_type": "device", "entity_id": "DEV_0001"},
    )
    assert res_400.status_code == 400

    # 404 Not Found on missing customer
    res_404 = client.post(
        "/api/agents/investigate",
        json={"entity_type": "customer", "entity_id": "CUST_99999"},
    )
    assert res_404.status_code == 404
