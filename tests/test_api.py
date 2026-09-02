"""Automated tests for FraudGraph Phase 5 FastAPI Backend endpoints."""

import pytest
from fastapi.testclient import TestClient

from backend.api.main import app


@pytest.fixture(scope="module")
def client():
    """Initializes FastAPI test client."""
    with TestClient(app) as test_client:
        yield test_client


def test_health_endpoint(client):
    """Verifies GET /api/health response schema and status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "FraudGraph"
    assert "version" in data


def test_dashboard_endpoint(client):
    """Verifies GET /api/dashboard returns real computed dataset statistics."""
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert data["total_customers"] == 2000
    assert data["total_transactions"] == 10000
    assert data["total_fraud_rings"] >= 5
    assert data["high_risk_customers_count"] >= 1
    assert "risk_distribution" in data
    assert "LOW" in data["risk_distribution"]
    assert "CRITICAL" in data["risk_distribution"]
    assert data["highest_risk_customer"]["entity_id"] is not None
    assert data["highest_risk_ring"]["entity_id"] is not None


def test_customers_pagination_and_filters(client):
    """Verifies customer pagination, limit bounds, and risk tier filtering."""
    # Default page
    resp = client.get("/api/customers?page=1&page_size=10")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 10
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert data["total"] == 2000

    # Risk level filter
    resp_crit = client.get("/api/customers?risk_level=CRITICAL")
    assert resp_crit.status_code == 200
    data_crit = resp_crit.json()
    for item in data_crit["items"]:
        assert item["risk_level"] == "CRITICAL"

    # Minimum risk score filter
    resp_score = client.get("/api/customers?minimum_risk_score=75.0")
    assert resp_score.status_code == 200
    data_score = resp_score.json()
    for item in data_score["items"]:
        assert item["risk_score"] >= 75.0

    # Search filter
    resp_search = client.get("/api/customers?search=FR_017")
    assert resp_search.status_code == 200
    data_search = resp_search.json()
    for item in data_search["items"]:
        assert "FR_017" in (item["ring_id"] or "") or "FR_017" in item["top_signal"]


def test_customer_detail_lookup_success(client):
    """Verifies GET /api/customers/{customer_id} returns full investigation profile."""
    resp = client.get("/api/customers/CUST_00028")
    assert resp.status_code == 200
    data = resp.json()
    assert data["customer_id"] == "CUST_00028"
    assert 0.0 <= data["risk_score"] <= 100.0
    assert data["risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    assert len(data["evidence"]) >= 1
    assert isinstance(data["timeline"], list)
    assert len(data["recommendations"]) >= 1


def test_customer_detail_lookup_404(client):
    """Verifies GET /api/customers/{customer_id} returns 404 for invalid customer ID."""
    resp = client.get("/api/customers/CUST_99999")
    assert resp.status_code == 404
    data = resp.json()
    assert data["error"] is True
    assert "not found" in data["message"].lower()


def test_transaction_lookup_success_and_404(client):
    """Verifies transaction detail lookup and 404 error handling."""
    resp_ok = client.get("/api/transactions/TXN_00001")
    assert resp_ok.status_code == 200
    data = resp_ok.json()
    assert data["transaction_id"] == "TXN_00001"
    assert data["amount"] > 0
    assert data["customer_id"] is not None

    resp_404 = client.get("/api/transactions/TXN_99999")
    assert resp_404.status_code == 404
    assert resp_404.json()["error"] is True


def test_fraud_rings_list(client):
    """Verifies GET /api/fraud-rings returns list of detected syndicates."""
    resp = client.get("/api/fraud-rings?page=1&page_size=20")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) >= 5
    assert data["items"][0]["ring_id"].startswith("FR_")
    assert data["items"][0]["risk_score"] > 0


def test_fraud_ring_detail_lookup(client):
    """Verifies GET /api/fraud-rings/{ring_id} returns members and infrastructure."""
    resp = client.get("/api/fraud-rings/FR_017")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ring_id"] == "FR_017"
    assert data["customer_count"] > 0
    assert len(data["members"]) > 0
    assert len(data["recommendations"]) >= 1


def test_fraud_ring_detail_404(client):
    """Verifies GET /api/fraud-rings/{ring_id} returns 404 for unknown ring."""
    resp = client.get("/api/fraud-rings/FR_999")
    assert resp.status_code == 404
    assert resp.json()["error"] is True


def test_investigation_endpoint(client):
    """Verifies GET /api/investigation/{entity_type}/{entity_id} structured report endpoint."""
    resp_cust = client.get("/api/investigation/customer/CUST_00028")
    assert resp_cust.status_code == 200
    data_cust = resp_cust.json()
    assert data_cust["entity_id"] == "CUST_00028"

    resp_ring = client.get("/api/investigation/ring/FR_017")
    assert resp_ring.status_code == 200
    data_ring = resp_ring.json()
    assert data_ring["entity_id"] == "FR_017"


def test_network_endpoint_customer(client):
    """Verifies GET /api/network/customer/{customer_id} returns Cytoscape nodes and edges."""
    resp = client.get("/api/network/customer/CUST_00028")
    assert resp.status_code == 200
    data = resp.json()
    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) >= 1
    assert data["center_node_id"] == "CUST_00028"
    assert "data" in data["nodes"][0]
    assert "id" in data["nodes"][0]["data"]


def test_network_endpoint_ring(client):
    """Verifies GET /api/network/ring/{ring_id} returns syndicate network."""
    resp = client.get("/api/network/ring/FR_017")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["nodes"]) >= 2
    assert data["center_node_id"] == "FR_017"


def test_invalid_entity_type_error_handling(client):
    """Verifies 400 Bad Request on invalid entity type parameters."""
    resp1 = client.get("/api/investigation/invalid_entity_type/123")
    assert resp1.status_code == 400
    assert resp1.json()["error"] is True

    resp2 = client.get("/api/network/unknown_type/123")
    assert resp2.status_code == 400
    assert resp2.json()["error"] is True
