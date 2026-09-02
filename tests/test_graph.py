"""Unit and integration test suite for FraudGraph Phase 2 Graph Intelligence Engine."""

import pytest
import pandas as pd
import numpy as np
import networkx as nx
from pathlib import Path

from backend.config.settings import get_settings
from backend.graph.graph_builder import GraphBuilder
from backend.graph.graph_features import GraphFeatureExtractor
from backend.graph.community_detection import CommunityDetector
from backend.graph.ring_detector import FraudRingDetector
from backend.graph.evaluation import GroundTruthEvaluator
from backend.graph.run_pipeline import run_pipeline


@pytest.fixture(scope="module")
def settings():
    return get_settings()


@pytest.fixture(scope="module")
def loaded_builder(settings):
    builder = GraphBuilder(data_dir=settings.raw_data_dir)
    builder.load_datasets()
    return builder


@pytest.fixture(scope="module")
def hetero_graph(loaded_builder):
    return loaded_builder.build_heterogeneous_graph()


@pytest.fixture(scope="module")
def customer_graph(loaded_builder):
    return loaded_builder.build_customer_projection_graph()


@pytest.fixture(scope="module")
def graph_features(hetero_graph, customer_graph, loaded_builder):
    extractor = GraphFeatureExtractor(hetero_graph, customer_graph, loaded_builder.datasets)
    return extractor.extract_features()


@pytest.fixture(scope="module")
def communities(customer_graph):
    detector = CommunityDetector(customer_graph, min_community_size=2)
    return detector.detect_communities()


def test_heterogeneous_graph_node_creation(hetero_graph):
    """Verify that all 7 heterogeneous node types are created with proper attributes."""
    node_types = set(nx.get_node_attributes(hetero_graph, "node_type").values())
    expected_types = {"Customer", "Transaction", "Device", "IP", "PaymentMethod", "Merchant", "Location"}
    assert expected_types.issubset(node_types), f"Missing node types: {expected_types - node_types}"

    # Verify specific entity nodes exist
    assert hetero_graph.has_node("CUST_00001")
    assert hetero_graph.has_node("TXN_00001")
    assert hetero_graph.has_node("DEV_0001")
    assert hetero_graph.has_node("IP_00001")
    assert hetero_graph.has_node("PM_0001")
    assert hetero_graph.has_node("MERCH_0001")
    assert hetero_graph.has_node("LOC_Mumbai")


def test_heterogeneous_graph_edge_creation(hetero_graph):
    """Verify all directed relational edge types exist in heterogeneous graph."""
    edge_types = set()
    for _, _, d in hetero_graph.edges(data=True):
        edge_types.add(d.get("edge_type"))

    expected_edges = {
        "INITIATED",
        "PAID_TO",
        "TRANSACTED_ON",
        "ROUTED_THROUGH",
        "PAID_WITH",
        "LOCATED_IN",
        "USES_DEVICE",
        "USES_IP",
        "USES_PAYMENT",
    }
    assert expected_edges.issubset(edge_types), f"Missing edge types: {expected_edges - edge_types}"


def test_ground_truth_exclusion_from_graph_metadata(hetero_graph):
    """Verify ground truth fraud labels are strictly excluded from graph nodes and edges."""
    for n, d in hetero_graph.nodes(data=True):
        assert "is_fraud" not in d, f"Ground truth 'is_fraud' found in node {n}"
        assert "fraud_ring_id" not in d, f"Ground truth 'fraud_ring_id' found in node {n}"
        assert "fraud_type" not in d, f"Ground truth 'fraud_type' found in node {n}"


def test_customer_projection_graph_structure(customer_graph):
    """Verify homogeneous customer projection graph connects customers with shared resources."""
    assert customer_graph.number_of_nodes() == 2000
    assert customer_graph.number_of_edges() > 0

    # Verify edge data contains resource linkage metadata
    sample_u, sample_v, data = next(iter(customer_graph.edges(data=True)))
    assert "weight" in data
    assert data["weight"] > 0
    assert "edge_type" in data


def test_graph_feature_extraction(graph_features):
    """Verify calculated graph features contain required structural and behavioral metrics."""
    assert isinstance(graph_features, pd.DataFrame)
    assert len(graph_features) == 2000

    required_features = {
        "customer_id",
        "degree",
        "weighted_degree",
        "pagerank",
        "betweenness_centrality",
        "clustering_coefficient",
        "connected_customers",
        "shared_device_count",
        "shared_ip_count",
        "shared_payment_count",
        "merchant_hhi",
        "transaction_count",
        "transaction_volume",
        "txn_velocity_per_day",
        "temporal_sync_score",
        "geographic_spread",
    }
    missing_features = required_features - set(graph_features.columns)
    assert not missing_features, f"Missing required graph features: {missing_features}"

    # Verify numerical ranges
    assert (graph_features["pagerank"] >= 0).all()
    assert (graph_features["betweenness_centrality"] >= 0).all()
    assert (graph_features["clustering_coefficient"] >= 0).all()
    assert (graph_features["clustering_coefficient"] <= 1.0).all()
    assert (graph_features["merchant_hhi"] >= 0).all()
    assert (graph_features["merchant_hhi"] <= 1.0).all()


def test_community_detection_modularity(communities):
    """Verify community detection partitions the customer network into non-trivial clusters."""
    assert len(communities) > 0

    total_clustered_nodes = 0
    for comm in communities:
        assert comm["customer_count"] >= 2
        assert len(comm["members"]) == comm["customer_count"]
        assert "density" in comm
        assert "internal_weight" in comm
        total_clustered_nodes += comm["customer_count"]

    assert total_clustered_nodes <= 2000


def test_fraud_ring_detection_and_scoring(graph_features, communities, loaded_builder):
    """Verify multi-signal risk scoring and fraud ring extraction."""
    ring_detector = FraudRingDetector(
        features_df=graph_features,
        communities=communities,
        datasets=loaded_builder.datasets,
        risk_threshold=50.0,
    )
    rings_df, members_df = ring_detector.detect_fraud_rings()

    assert isinstance(rings_df, pd.DataFrame)
    assert isinstance(members_df, pd.DataFrame)
    assert not rings_df.empty
    assert not members_df.empty

    # Verify risk scores normalized to 0 - 100
    assert (rings_df["risk_score"] >= 0).all()
    assert (rings_df["risk_score"] <= 100).all()
    assert (members_df["individual_risk_score"] >= 0).all()
    assert (members_df["individual_risk_score"] <= 100).all()
    assert (members_df["network_risk_score"] >= 0).all()
    assert (members_df["network_risk_score"] <= 100).all()

    # Verify core members are identified
    assert "is_core_member" in members_df.columns
    assert members_df["is_core_member"].dtype == bool


def test_individual_vs_network_risk_discrepancy(graph_features, communities, loaded_builder):
    """Verify that some members have low individual risk but high network risk (FraudGraph core thesis)."""
    ring_detector = FraudRingDetector(
        features_df=graph_features,
        communities=communities,
        datasets=loaded_builder.datasets,
        risk_threshold=50.0,
    )
    _, members_df = ring_detector.detect_fraud_rings()

    # Find accounts where individual risk < 35 but network risk >= 60
    low_ind_high_net = members_df[
        (members_df["individual_risk_score"] < 35.0) & (members_df["network_risk_score"] >= 60.0)
    ]
    assert len(low_ind_high_net) > 0, "Expected low-individual risk members embedded in high-risk rings."


def test_legitimate_shared_resource_false_positive_resistance(graph_features, loaded_builder):
    """Verify that a synthetic community sharing only one residential IP receives low network risk."""
    # Synthetic community sharing only 1 residential IP
    single_signal_comm = [{
        "community_id": "COMM_TEST",
        "members": ["CUST_00001", "CUST_00002"],
        "customer_count": 2,
        "edge_count": 1,
        "density": 1.0,
        "internal_weight": 1.0,
        "shared_devices": [],
        "shared_ips": ["IP_00001"],  # Residential IP
        "shared_pms": [],
        "shared_device_count": 0,
        "shared_ip_count": 1,
        "shared_payment_count": 0,
        "co_transaction_count": 0,
    }]

    ring_detector = FraudRingDetector(
        features_df=graph_features,
        communities=single_signal_comm,
        datasets=loaded_builder.datasets,
        risk_threshold=50.0,
    )
    rings_df, _ = ring_detector.detect_fraud_rings()

    # Should not trigger high risk fraud ring
    assert rings_df.empty, "Single shared residential IP should not automatically be classified as a fraud ring."


def test_graph_export_dataframes(loaded_builder):
    """Verify graph nodes and edges export to DataFrames for frontend/Cytoscape ingestion."""
    nodes_df, edges_df = loaded_builder.export_graph_to_dataframes()

    assert isinstance(nodes_df, pd.DataFrame)
    assert isinstance(edges_df, pd.DataFrame)

    assert set(nodes_df.columns) == {"node_id", "node_type", "label", "metadata"}
    assert set(edges_df.columns) == {"source", "target", "edge_type", "weight", "metadata"}

    assert len(nodes_df) >= 14000
    assert len(edges_df) >= 80000


def test_pipeline_execution_and_artifacts(settings):
    """Verify full pipeline execution and generation of all processed CSV artifacts."""
    summary = run_pipeline()

    assert summary["transactions_analyzed"] == 10000
    assert summary["customers_analyzed"] == 2000
    assert summary["communities_detected"] > 0
    assert summary["suspicious_rings_detected"] > 0
    assert summary["evaluation"]["ring_detection_rate_pct"] >= 80.0

    # Verify processed files exist
    processed_dir = settings.processed_data_dir
    assert (processed_dir / "fraud_rings.csv").exists()
    assert (processed_dir / "ring_members.csv").exists()
    assert (processed_dir / "graph_nodes.csv").exists()
    assert (processed_dir / "graph_edges.csv").exists()
