"""Unit and integration test suite for FraudGraph Phase 4 Explainable AI & Investigation Engine."""

import os
import json
import pytest
import numpy as np
import pandas as pd
from pathlib import Path

from backend.config.settings import get_settings
from backend.graph.graph_builder import GraphBuilder
from backend.graph.graph_features import GraphFeatureExtractor
from backend.graph.ring_detector import FraudRingDetector
from backend.graph.community_detection import CommunityDetector
from backend.explainability.evidence_engine import EvidenceEngine
from backend.explainability.feature_explanations import FeatureExplainer
from backend.explainability.network_explanations import NetworkExplainer
from backend.explainability.investigation_engine import InvestigationEngine
from backend.explainability.report_generator import ReportGenerator
from backend.explainability.llm_explainer import LLMExplainer


@pytest.fixture(scope="module")
def explainability_fixture():
    """Builds and caches graphs, models, and investigation engine for testing."""
    settings = get_settings()
    builder = GraphBuilder(data_dir=settings.raw_data_dir)
    datasets = builder.load_datasets()
    H = builder.build_heterogeneous_graph(datasets)
    G_cust = builder.build_customer_projection_graph(datasets)
    extractor = GraphFeatureExtractor(H, G_cust, datasets)
    graph_features_df = extractor.extract_features()

    detector = CommunityDetector(G_cust, min_community_size=2)
    communities = detector.detect_communities()
    ring_detector = FraudRingDetector(
        features_df=graph_features_df,
        communities=communities,
        datasets=datasets,
        risk_threshold=50.0,
    )
    rings_df, members_df = ring_detector.detect_fraud_rings()

    engine = InvestigationEngine(
        datasets=datasets,
        H=H,
        G_cust=G_cust,
        graph_features_df=graph_features_df,
        rings_df=rings_df,
        members_df=members_df,
    )

    return {
        "datasets": datasets,
        "H": H,
        "G_cust": G_cust,
        "graph_features_df": graph_features_df,
        "rings_df": rings_df,
        "members_df": members_df,
        "engine": engine,
    }


def test_evidence_engine_customer_explanation(explainability_fixture):
    """Verifies that EvidenceEngine produces valid Layer 1 structured evidence for a customer."""
    engine = explainability_fixture["engine"]
    cust_id = "CUST_00001"

    exp = engine.evidence_engine.explain_customer(cust_id)
    assert "entity_id" in exp
    assert exp["entity_id"] == cust_id
    assert exp["entity_type"] == "customer"
    assert 0.0 <= exp["risk_score"] <= 100.0
    assert exp["risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    assert exp["explanation_confidence"] in ["LOW", "MEDIUM", "HIGH"]
    assert isinstance(exp["evidence"], list)
    assert isinstance(exp["contributing_signals"], list)
    assert isinstance(exp["network_details"], dict)


def test_evidence_engine_transaction_explanation(explainability_fixture):
    """Verifies that EvidenceEngine produces valid evidence for an individual transaction."""
    engine = explainability_fixture["engine"]
    txn_id = "TXN_00001"

    exp = engine.evidence_engine.explain_transaction(txn_id)
    assert "entity_id" in exp
    assert exp["entity_id"] == txn_id
    assert exp["entity_type"] == "transaction"
    assert "customer_id" in exp
    assert "amount" in exp
    assert 0.0 <= exp["risk_score"] <= 100.0


def test_evidence_engine_fraud_ring_explanation(explainability_fixture):
    """Verifies that EvidenceEngine produces structured dossier for a detected fraud ring."""
    engine = explainability_fixture["engine"]
    rings_df = explainability_fixture["rings_df"]

    if not rings_df.empty:
        ring_id = str(rings_df.iloc[0]["ring_id"])
        exp = engine.evidence_engine.explain_fraud_ring(ring_id)
        assert exp["entity_id"] == ring_id
        assert exp["entity_type"] == "fraud_ring"
        assert 0.0 <= exp["risk_score"] <= 100.0
        assert "customer_count" in exp
        assert "shared_devices_count" in exp
        assert isinstance(exp["evidence"], list)


def test_feature_explainer_risk_and_protective_signals():
    """Verifies that FeatureExplainer isolates both positive risk signals and protective factors."""
    explainer = FeatureExplainer()

    # Spiking transaction with proxy IP
    risky_txn = pd.Series({
        "amount": 50000.0,
        "customer_avg_amount": 5000.0,
        "customer_velocity_per_day": 8.5,
        "is_remote_city": 1,
        "ip_is_proxy": 1,
        "hour_of_day": 3,
        "account_age_days": 15,
        "city": "Mumbai",
        "home_city": "Delhi",
    })
    res_risky = explainer.explain_transaction_features(risky_txn, model_prob=0.92, anomaly_score=85.0)
    assert res_risky["total_risk_signals"] >= 4
    signal_names = [s["signal"] for s in res_risky["risk_signals"]]
    assert "amount_spike" in signal_names
    assert "proxy_ip_routing" in signal_names
    assert "supervised_model_risk" in signal_names

    # Normal benign transaction
    benign_txn = pd.Series({
        "amount": 2500.0,
        "customer_avg_amount": 2400.0,
        "customer_velocity_per_day": 0.5,
        "is_remote_city": 0,
        "ip_is_proxy": 0,
        "hour_of_day": 14,
        "account_age_days": 400,
        "city": "Bangalore",
        "home_city": "Bangalore",
    })
    res_benign = explainer.explain_transaction_features(benign_txn, model_prob=0.05, anomaly_score=20.0)
    assert res_benign["total_protective_signals"] >= 2
    prot_names = [p["signal"] for p in res_benign["protective_signals"]]
    assert "consistent_amount" in prot_names
    assert "mature_account" in prot_names


def test_network_explainer_graph_linkages(explainability_fixture):
    """Verifies that NetworkExplainer extracts shared devices and connected accounts."""
    engine = explainability_fixture["engine"]
    cust_id = "CUST_00001"

    net_exp = engine.evidence_engine.network_explainer.explain_customer_network(cust_id)
    assert net_exp["customer_id"] == cust_id
    assert "degree" in net_exp
    assert "shared_devices" in net_exp
    assert "shared_payments" in net_exp
    assert "connected_neighbors" in net_exp


def test_investigation_timeline_generation(explainability_fixture):
    """Verifies chronological ordering and burst event detection in transaction timelines."""
    engine = explainability_fixture["engine"]
    cust_id = "CUST_00001"

    timeline = engine.build_investigation_timeline(cust_id)
    assert isinstance(timeline, list)
    if len(timeline) >= 2:
        # Check chronological order
        t0 = pd.to_datetime(timeline[0]["timestamp"])
        t1 = pd.to_datetime(timeline[1]["timestamp"])
        assert t0 <= t1
        assert "is_burst" in timeline[1]
        assert "tags" in timeline[1]


def test_investigator_recommendations_neutrality_and_grounding(explainability_fixture):
    """Verifies that investigator recommendations use neutral action verbs."""
    engine = explainability_fixture["engine"]
    exp = engine.explain_entity("CUST_00001")

    recommendations = exp.get("recommendations", [])
    assert len(recommendations) >= 1

    forbidden_words = {"arrest", "convict", "terminate immediately", "guilty"}
    for rec in recommendations:
        for fw in forbidden_words:
            assert fw not in rec.lower(), f"Non-neutral recommendation found: {rec}"


def test_deterministic_reproducibility(explainability_fixture):
    """Verifies that duplicate calls on the same entity produce identical outputs."""
    engine = explainability_fixture["engine"]
    cust_id = "CUST_00001"

    exp1 = engine.explain_entity(cust_id)
    exp2 = engine.explain_entity(cust_id)

    assert exp1["risk_score"] == exp2["risk_score"]
    assert exp1["risk_level"] == exp2["risk_level"]
    assert exp1["explanation_confidence"] == exp2["explanation_confidence"]
    assert len(exp1["evidence"]) == len(exp2["evidence"])
    assert exp1["investigation_report_markdown"] == exp2["investigation_report_markdown"]


def test_explanation_confidence_levels(explainability_fixture):
    """Verifies explanation confidence categorization logic."""
    engine = explainability_fixture["engine"]
    ev_engine = engine.evidence_engine

    # High confidence: multiple corroborating sources
    c_high = ev_engine.calculate_explanation_confidence(
        risk_signals=[{"signal": "amount_spike"}, {"signal": "velocity"}],
        network_signals=[{"signal": "shared_device"}, {"signal": "shared_pm"}],
    )
    assert c_high == "HIGH"

    # Medium confidence: partial corroboration
    c_med = ev_engine.calculate_explanation_confidence(
        risk_signals=[{"signal": "amount_spike"}],
        network_signals=[],
    )
    assert c_med == "LOW"

    c_med2 = ev_engine.calculate_explanation_confidence(
        risk_signals=[{"signal": "amount_spike"}, {"signal": "velocity"}],
        network_signals=[],
    )
    assert c_med2 == "MEDIUM"


def test_report_generator_formatting():
    """Verifies that ReportGenerator produces structured markdown reports."""
    mock_cust_data = {
        "entity_id": "CUST_99999",
        "risk_score": 88.5,
        "risk_level": "CRITICAL",
        "explanation_confidence": "HIGH",
        "associated_ring_id": "FR_001",
        "member_role": "CORE_MEMBER",
        "total_transactions": 12,
        "total_spend": 350000.0,
        "evidence": [
            {"severity": "CRITICAL", "description": "Shared hardware device Dev_01 with 6 other accounts."},
            {"severity": "HIGH", "description": "Shared payment card PM_02 with 4 accounts."},
        ],
        "network_details": {
            "shared_devices": [{"device_id": "DEV_01", "shared_with_count": 6, "connected_customers": ["CUST_001", "CUST_002"]}],
            "shared_payments": [{"payment_method_id": "PM_02", "shared_with_count": 4, "connected_customers": ["CUST_001", "CUST_002"]}],
        },
        "protective_factors": [],
        "recommendations": ["Review authorization logs on shared payment instrument PM_02."],
    }

    report = ReportGenerator.generate_customer_report(mock_cust_data)
    assert "FRAUDGRAPH FORENSIC INVESTIGATION REPORT" in report
    assert "CUST_99999" in report
    assert "88.5 / 100" in report
    assert "CRITICAL" in report
    assert "Shared hardware device Dev_01" in report


def test_llm_explainer_isolation_and_fallback():
    """Verifies that LLMExplainer functions safely and falls back deterministically without API keys."""
    # Ensure no API key in test environment
    explainer = LLMExplainer(api_key="")
    assert not explainer.is_available

    mock_evidence = {
        "entity_id": "CUST_00001",
        "entity_type": "customer",
        "risk_score": 75.0,
        "risk_level": "HIGH",
        "explanation_confidence": "MEDIUM",
        "evidence": [{"severity": "HIGH", "description": "Shared proxy IP address."}],
    }

    narrative = explainer.explain(mock_evidence)
    assert isinstance(narrative, str)
    assert "FRAUDGRAPH FORENSIC INVESTIGATION REPORT" in narrative
    assert "CUST_00001" in narrative


def test_investigation_reports_and_index_artifacts_exist():
    """Verifies that investigation index, summary, and report directory exist and are populated."""
    settings = get_settings()
    processed_dir = settings.processed_data_dir
    reports_dir = processed_dir / "investigation_reports"

    assert (processed_dir / "investigation_index.json").exists()
    assert (processed_dir / "investigation_summary.json").exists()
    assert reports_dir.exists()

    with open(processed_dir / "investigation_index.json", "r", encoding="utf-8") as f:
        idx = json.load(f)
        assert len(idx) >= 2000

    with open(processed_dir / "investigation_summary.json", "r", encoding="utf-8") as f:
        summary = json.load(f)
        assert "highest_risk_ring" in summary
        assert "highest_risk_customer" in summary
