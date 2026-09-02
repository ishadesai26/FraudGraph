"""End-to-end graph construction, community detection, and fraud-ring pipeline."""

import sys
from pathlib import Path
import pandas as pd

# Ensure backend package can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.config.settings import get_settings
from backend.graph.graph_builder import GraphBuilder
from backend.graph.graph_features import GraphFeatureExtractor
from backend.graph.community_detection import CommunityDetector
from backend.graph.ring_detector import FraudRingDetector
from backend.graph.evaluation import GroundTruthEvaluator


def run_pipeline() -> dict:
    """Executes full Phase 2 graph analytics and fraud detection pipeline."""
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    settings = get_settings()
    processed_dir = settings.processed_data_dir
    processed_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("FRAUDGRAPH PHASE 2: GRAPH CONSTRUCTION & RING DETECTION")
    print("=" * 60)

    # 1. Load data and build graphs
    print("\n[1/5] Building Heterogeneous & Customer Projection Graphs...")
    builder = GraphBuilder(data_dir=settings.raw_data_dir)
    datasets = builder.load_datasets()
    H = builder.build_heterogeneous_graph(datasets)
    G_cust = builder.build_customer_projection_graph(datasets)

    num_txns = len(datasets["transactions"])
    num_custs = len(datasets["customers"])
    num_h_nodes = H.number_of_nodes()
    num_h_edges = H.number_of_edges()
    num_cg_edges = G_cust.number_of_edges()

    print(f"  Heterogeneous Graph Nodes: {num_h_nodes:,}")
    print(f"  Heterogeneous Graph Edges: {num_h_edges:,}")
    print(f"  Customer Projection Edges: {num_cg_edges:,}")

    # 2. Extract topological & behavioral features
    print("\n[2/5] Extracting Graph Features & Centrality Metrics...")
    extractor = GraphFeatureExtractor(H, G_cust, datasets)
    features_df = extractor.extract_features()
    print(f"  Extracted {features_df.shape[1]} features across {len(features_df)} customer accounts.")

    # 3. Detect cohesive communities
    print("\n[3/5] Detecting Connected Communities (Modularity Maximization)...")
    detector = CommunityDetector(G_cust, min_community_size=2)
    communities = detector.detect_communities()
    print(f"  Detected {len(communities)} multi-customer communities.")

    # 4. Multi-signal risk scoring and fraud ring detection
    print("\n[4/5] Scoring Network Risk & Isolating Fraud Rings...")
    ring_detector = FraudRingDetector(
        features_df=features_df,
        communities=communities,
        datasets=datasets,
        risk_threshold=50.0,
    )
    rings_df, members_df = ring_detector.detect_fraud_rings()
    num_rings = len(rings_df)
    num_flagged_members = len(members_df) if not members_df.empty else 0

    print(f"  Identified {num_rings} suspicious coordinated fraud rings.")
    print(f"  Total flagged ring members: {num_flagged_members}")

    # 5. Export processed CSVs
    print("\n[5/5] Exporting Artifacts to data/processed/...")
    nodes_df, edges_df = builder.export_graph_to_dataframes()

    rings_path = processed_dir / "fraud_rings.csv"
    members_path = processed_dir / "ring_members.csv"
    nodes_path = processed_dir / "graph_nodes.csv"
    edges_path = processed_dir / "graph_edges.csv"

    rings_df.to_csv(rings_path, index=False)
    members_df.to_csv(members_path, index=False)
    nodes_df.to_csv(nodes_path, index=False)
    edges_df.to_csv(edges_path, index=False)

    print(f"  Saved: {rings_path.name} ({len(rings_df)} rows)")
    print(f"  Saved: {members_path.name} ({len(members_df)} rows)")
    print(f"  Saved: {nodes_path.name} ({len(nodes_df)} rows)")
    print(f"  Saved: {edges_path.name} ({len(edges_df)} rows)")

    # Ground truth evaluation
    evaluator = GroundTruthEvaluator(rings_df, members_df, datasets)
    eval_results = evaluator.evaluate()

    # Formatted Summary
    highest_risk_ring = rings_df.iloc[0]["ring_id"] if not rings_df.empty else "N/A"
    highest_risk_score = rings_df.iloc[0]["risk_score"] if not rings_df.empty else 0.0
    ring_tx_vol = rings_df["transaction_volume"].sum() if not rings_df.empty else 0.0

    print("\n" + "=" * 60)
    print("GRAPH PIPELINE EXECUTION SUMMARY")
    print("=" * 60)
    print(f"Transactions analyzed: {num_txns:,}")
    print(f"Customers analyzed: {num_custs:,}")
    print(f"Graph nodes: {num_h_nodes:,}")
    print(f"Graph edges: {num_h_edges:,}")
    print(f"Communities detected: {len(communities)}")
    print(f"Suspicious rings detected: {num_rings}")
    print(f"Highest-risk ring: {highest_risk_ring}")
    print(f"Highest network risk: {highest_risk_score}/100")
    try:
        print(f"Transaction volume associated with suspicious rings: ₹{ring_tx_vol:,.2f}")
    except UnicodeEncodeError:
        print(f"Transaction volume associated with suspicious rings: INR {ring_tx_vol:,.2f}")

    print("\n--- Ground-Truth Evaluation Metrics ---")
    print(f"Injected Fraud Rings Detected: {eval_results['detected_gt_rings']}/{eval_results['total_gt_rings']} ({eval_results['ring_detection_rate_pct']}%)")
    cm = eval_results["customer_metrics"]
    print(f"Customer Precision: {cm['precision_pct']}% | Recall: {cm['recall_pct']}% | F1 Score: {cm['f1_score']}")
    tm = eval_results["transaction_metrics"]
    print(f"Transaction Precision: {tm['precision_pct']}% | Recall: {tm['recall_pct']}% | F1 Score: {tm['f1_score']}")
    print("=" * 60 + "\n")

    return {
        "transactions_analyzed": num_txns,
        "customers_analyzed": num_custs,
        "graph_nodes": num_h_nodes,
        "graph_edges": num_h_edges,
        "communities_detected": len(communities),
        "suspicious_rings_detected": num_rings,
        "highest_risk_ring": highest_risk_ring,
        "highest_network_risk": highest_risk_score,
        "ring_transaction_volume": ring_tx_vol,
        "evaluation": eval_results,
    }


if __name__ == "__main__":
    run_pipeline()
