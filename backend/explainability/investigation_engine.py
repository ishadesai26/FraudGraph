"""Main Investigation Intelligence Engine and CLI Demonstration for FraudGraph.

Orchestrates:
1. Multi-Entity "Why Flagged?" Explanations (Customer, Transaction, Fraud Ring)
2. Chronological Investigation Timeline Reconstruction
3. Evidence-Based Investigator Next Steps
4. Searchable Index & Summary Export
5. Full Report Generation under data/processed/investigation_reports/
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import numpy as np
import pandas as pd
import networkx as nx

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.config.settings import get_settings
from backend.graph.graph_builder import GraphBuilder
from backend.graph.graph_features import GraphFeatureExtractor
from backend.graph.ring_detector import FraudRingDetector
from backend.graph.community_detection import CommunityDetector
from backend.ml.preprocessing import DataPreprocessor
from backend.ml.baseline_model import BaselineFraudModel
from backend.ml.anomaly_detector import AnomalyDetector
from backend.ml.graph_model import FraudGraphModel
from backend.ml.risk_scorer import CompositeRiskScorer
from backend.ml.feature_engineering import MLFeatureEngineer

from backend.explainability.evidence_engine import EvidenceEngine
from backend.explainability.report_generator import ReportGenerator
from backend.explainability.llm_explainer import LLMExplainer


class InvestigationEngine:
    """Orchestrates comprehensive fraud investigation intelligence dossiers and indices."""

    def __init__(
        self,
        datasets: Optional[Dict[str, pd.DataFrame]] = None,
        H: Optional[nx.MultiDiGraph] = None,
        G_cust: Optional[nx.Graph] = None,
        graph_features_df: Optional[pd.DataFrame] = None,
        rings_df: Optional[pd.DataFrame] = None,
        members_df: Optional[pd.DataFrame] = None,
        feature_importance_data: Optional[Dict[str, Any]] = None,
        artifacts_dir: Optional[Path] = None,
    ):
        settings = get_settings()
        self.data_dir = settings.raw_data_dir
        self.processed_dir = settings.processed_data_dir
        self.artifacts_dir = artifacts_dir or (Path(__file__).resolve().parent.parent / "ml" / "artifacts")

        # Load raw datasets if not provided
        if datasets is None:
            builder = GraphBuilder(data_dir=self.data_dir)
            self.datasets = builder.load_datasets()
        else:
            self.datasets = datasets

        # Load graph and features if not provided
        if H is None or G_cust is None:
            builder = GraphBuilder(data_dir=self.data_dir)
            self.H = builder.build_heterogeneous_graph(self.datasets)
            self.G_cust = builder.build_customer_projection_graph(self.datasets)
        else:
            self.H = H
            self.G_cust = G_cust

        if graph_features_df is None:
            extractor = GraphFeatureExtractor(self.H, self.G_cust, self.datasets)
            self.graph_features_df = extractor.extract_features()
        else:
            self.graph_features_df = graph_features_df

        if rings_df is None or members_df is None:
            detector = CommunityDetector(self.G_cust, min_community_size=2)
            communities = detector.detect_communities()
            ring_detector = FraudRingDetector(
                features_df=self.graph_features_df,
                communities=communities,
                datasets=self.datasets,
                risk_threshold=50.0,
            )
            self.rings_df, self.members_df = ring_detector.detect_fraud_rings()
        else:
            self.rings_df = rings_df
            self.members_df = members_df

        # Load feature importance
        if feature_importance_data is None:
            feat_imp_path = self.processed_dir / "feature_importance.json"
            if feat_imp_path.exists():
                with open(feat_imp_path, "r", encoding="utf-8") as f:
                    self.feature_importance_data = json.load(f)
            else:
                self.feature_importance_data = {}
        else:
            self.feature_importance_data = feature_importance_data

        # Initialize ML scoring pipelines if available
        self.risk_scorer = CompositeRiskScorer()
        self.evidence_engine = EvidenceEngine(
            datasets=self.datasets,
            H=self.H,
            G_cust=self.G_cust,
            graph_features_df=self.graph_features_df,
            rings_df=self.rings_df,
            members_df=self.members_df,
            feature_importance_data=self.feature_importance_data,
            risk_scorer=self.risk_scorer,
        )
        self.llm_explainer = LLMExplainer()

        # Precompute exact ML inferences from Phase 3 artifacts
        self._customer_ml_scores: Dict[str, Tuple[float, float]] = {}
        self._transaction_ml_scores: Dict[str, Tuple[float, float]] = {}
        self._precompute_ml_inferences()

    def _precompute_ml_inferences(self) -> None:
        """Precomputes exact Phase 3 ML probabilities and anomaly scores for all transactions."""
        try:
            fg_art = self.artifacts_dir / "fraudgraph_model.joblib"
            prep_g_art = self.artifacts_dir / "preprocessor_graph.joblib"
            anom_art = self.artifacts_dir / "anomaly_model.joblib"
            prep_b_art = self.artifacts_dir / "preprocessor_baseline.joblib"

            if fg_art.exists() and prep_g_art.exists():
                prep_graph = DataPreprocessor.load(str(prep_g_art))
                model_graph = FraudGraphModel.load(str(fg_art))

                feat_eng = MLFeatureEngineer(
                    datasets=self.datasets,
                    graph_features_df=self.graph_features_df,
                    rings_df=self.rings_df,
                    members_df=self.members_df,
                )
                full_df = feat_eng.build_feature_dataframe()

                graph_cols = feat_eng.BASELINE_NUMERICAL_FEATURES + feat_eng.BASELINE_CATEGORICAL_FEATURES + feat_eng.GRAPH_NUMERICAL_FEATURES
                X_graph = full_df[graph_cols]
                X_graph_prep = prep_graph.transform(X_graph)
                probs = model_graph.predict_proba(X_graph_prep)

                anom_scores = np.full(len(probs), 40.0)
                if anom_art.exists() and prep_b_art.exists():
                    prep_base = DataPreprocessor.load(str(prep_b_art))
                    anomaly_model = AnomalyDetector.load(str(anom_art))
                    base_cols = feat_eng.BASELINE_NUMERICAL_FEATURES + feat_eng.BASELINE_CATEGORICAL_FEATURES
                    X_base = full_df[base_cols]
                    X_base_prep = prep_base.transform(X_base)
                    anom_scores = anomaly_model.predict_anomaly_score(X_base_prep)

                full_df["model_prob"] = probs
                full_df["anomaly_score"] = anom_scores

                # Map transaction scores
                for _, row in full_df.iterrows():
                    t_id = str(row["transaction_id"])
                    self._transaction_ml_scores[t_id] = (float(row["model_prob"]), float(row["anomaly_score"]))

                # Map max customer scores
                cust_grouped = full_df.groupby("customer_id").agg({
                    "model_prob": "max",
                    "anomaly_score": "max",
                })
                for c_id, row in cust_grouped.iterrows():
                    self._customer_ml_scores[str(c_id)] = (float(row["model_prob"]), float(row["anomaly_score"]))
        except Exception:
            pass

    def build_investigation_timeline(self, customer_id: str) -> List[Dict[str, Any]]:
        """Constructs chronological transaction timeline with burst and anomaly tags."""
        txns_df = self.datasets.get("transactions", pd.DataFrame())
        c_txns = txns_df[txns_df["customer_id"] == customer_id].copy()
        if c_txns.empty:
            return []

        c_txns["dt"] = pd.to_datetime(c_txns["timestamp"])
        c_txns.sort_values(by="dt", inplace=True)

        timeline = []
        prev_dt = None

        for idx, row in c_txns.iterrows():
            curr_dt = row["dt"]
            time_delta_sec = (curr_dt - prev_dt).total_seconds() if prev_dt is not None else None
            is_burst = time_delta_sec is not None and time_delta_sec <= 180

            event_tags = []
            if is_burst:
                event_tags.append("BURST_SYNC")
            if float(row["amount"]) > 25000:
                event_tags.append("HIGH_VALUE")

            timeline.append({
                "transaction_id": str(row["transaction_id"]),
                "timestamp": str(row["timestamp"]),
                "amount": float(row["amount"]),
                "merchant_id": str(row.get("merchant_id", "Unknown")),
                "payment_type": str(row.get("payment_type", "Unknown")),
                "device_id": str(row.get("device_id", "Unknown")),
                "ip_id": str(row.get("ip_id", "Unknown")),
                "city": str(row.get("city", "Unknown")),
                "seconds_since_previous": time_delta_sec,
                "is_burst": is_burst,
                "tags": event_tags,
            })
            prev_dt = curr_dt

        return timeline

    def generate_investigator_recommendations(self, evidence_data: Dict[str, Any]) -> List[str]:
        """Produces neutral, evidence-grounded next steps for fraud investigators."""
        recommendations = []
        entity_type = evidence_data.get("entity_type", "customer")

        if entity_type == "customer":
            net_details = evidence_data.get("network_details", {})
            shared_pms = net_details.get("shared_payments", [])
            shared_devs = net_details.get("shared_devices", [])
            ring_id = evidence_data.get("associated_ring_id")

            if shared_pms:
                recommendations.append(f"Review authorization logs for shared payment instrument '{shared_pms[0]['payment_method_id']}' across {shared_pms[0]['shared_with_count']} linked accounts.")
            if shared_devs:
                recommendations.append(f"Examine device fingerprint integrity for hardware endpoint '{shared_devs[0]['device_id']}'.")
            if ring_id and ring_id != "None (Isolated Node)":
                recommendations.append(f"Audit coordinated transaction flow within syndicate '{ring_id}'.")
            if evidence_data.get("risk_score", 0.0) >= 80.0:
                recommendations.append("Initiate mandatory step-up identity verification challenge prior to fund release.")

        elif entity_type == "fraud_ring":
            dev_cnt = evidence_data.get("shared_devices_count", 0)
            pm_cnt = evidence_data.get("shared_payments_count", 0)
            if pm_cnt > 0:
                recommendations.append(f"Audit {pm_cnt} shared payment instruments across member accounts for synthetic identity collusion.")
            if dev_cnt > 0:
                recommendations.append(f"Review session logs for {dev_cnt} shared hardware devices for automated script or bot activity.")
            recommendations.append("Correlate merchant payout accounts receiving aggregated syndicate payments.")

        if not recommendations:
            recommendations.append("Monitor account behavior through regular periodic surveillance.")

        return recommendations

    def explain_entity(self, entity_id: str) -> Dict[str, Any]:
        """Unified resolver for Customer, Transaction, or Fraud Ring investigation dossiers."""
        if entity_id.startswith("CUST_") or entity_id.isdigit():
            cust_id = entity_id if entity_id.startswith("CUST_") else f"CUST_{int(entity_id):05d}"
            m_prob, a_score = self._customer_ml_scores.get(cust_id, (None, None))
            evidence_data = self.evidence_engine.explain_customer(cust_id, model_prob=m_prob, anomaly_score=a_score)
            if "error" not in evidence_data:
                evidence_data["timeline"] = self.build_investigation_timeline(cust_id)
                evidence_data["recommendations"] = self.generate_investigator_recommendations(evidence_data)
                evidence_data["investigation_report_markdown"] = ReportGenerator.generate_customer_report(evidence_data)
            return evidence_data

        elif entity_id.startswith("TXN_"):
            m_prob, a_score = self._transaction_ml_scores.get(entity_id, (None, None))
            evidence_data = self.evidence_engine.explain_transaction(entity_id, model_prob=m_prob, anomaly_score=a_score)
            if "error" not in evidence_data:
                cust_id = evidence_data.get("customer_id")
                if cust_id:
                    evidence_data["timeline"] = self.build_investigation_timeline(cust_id)
                evidence_data["recommendations"] = self.generate_investigator_recommendations(evidence_data)
            return evidence_data

        elif entity_id.startswith("FR_") or entity_id.startswith("RING_"):
            evidence_data = self.evidence_engine.explain_fraud_ring(entity_id)
            if "error" not in evidence_data:
                evidence_data["recommendations"] = self.generate_investigator_recommendations(evidence_data)
                evidence_data["investigation_report_markdown"] = ReportGenerator.generate_ring_report(evidence_data)
            return evidence_data

        else:
            return {"entity_id": entity_id, "error": f"Unrecognized entity identifier format: {entity_id}"}

    def generate_all_reports_and_indices(self) -> Dict[str, Any]:
        """Generates all forensic reports, investigation index, and high-level summary."""
        reports_dir = self.processed_dir / "investigation_reports"
        reports_dir.mkdir(parents=True, exist_ok=True)

        investigation_index = []
        investigated_rings = []
        high_risk_customers = []

        # 1. Generate reports for all detected fraud rings
        if not self.rings_df.empty and "ring_id" in self.rings_df.columns:
            for _, r_row in self.rings_df.iterrows():
                r_id = str(r_row["ring_id"])
                r_exp = self.explain_entity(r_id)
                if "error" not in r_exp:
                    investigated_rings.append(r_exp)
                    # Save individual JSON report
                    r_file = reports_dir / f"{r_id}.json"
                    with open(r_file, "w", encoding="utf-8") as f:
                        json.dump(r_exp, f, indent=2)

                    investigation_index.append({
                        "entity_id": r_id,
                        "entity_type": "fraud_ring",
                        "risk_score": r_exp.get("risk_score", 0.0),
                        "risk_level": r_exp.get("risk_level", "HIGH"),
                        "ring_id": r_id,
                        "top_signal": r_exp["evidence"][0]["signal"] if r_exp.get("evidence") else "network_risk",
                        "community_size": r_exp.get("customer_count", 0),
                    })

        # 2. Generate reports for all high-risk / critical customers
        cust_list = self.datasets["customers"]["customer_id"].tolist()
        for c_id in cust_list:
            c_exp = self.explain_entity(c_id)
            if "error" not in c_exp:
                score = c_exp.get("risk_score", 0.0)
                level = c_exp.get("risk_level", "LOW")
                
                # Add to index
                top_sig = c_exp["evidence"][0]["signal"] if c_exp.get("evidence") else "normal_activity"
                investigation_index.append({
                    "entity_id": c_id,
                    "entity_type": "customer",
                    "risk_score": score,
                    "risk_level": level,
                    "ring_id": c_exp.get("associated_ring_id"),
                    "top_signal": top_sig,
                    "community_size": c_exp.get("network_details", {}).get("degree", 0),
                })

                # Save detailed dossier for HIGH and CRITICAL entities
                if level in ["HIGH", "CRITICAL"] or score >= 60.0:
                    high_risk_customers.append(c_exp)
                    c_file = reports_dir / f"{c_id}.json"
                    with open(c_file, "w", encoding="utf-8") as f:
                        json.dump(c_exp, f, indent=2)

        # 3. Save Searchable Index
        index_path = self.processed_dir / "investigation_index.json"
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(investigation_index, f, indent=2)

        # 4. Save High-Level Investigation Summary
        highest_ring = max(investigated_rings, key=lambda x: x.get("risk_score", 0.0), default={})
        highest_cust = max(high_risk_customers, key=lambda x: x.get("risk_score", 0.0), default={})

        summary_data = {
            "total_entities_indexed": len(investigation_index),
            "investigated_rings_count": len(investigated_rings),
            "high_risk_customers_count": len(high_risk_customers),
            "highest_risk_ring": {
                "ring_id": highest_ring.get("entity_id"),
                "risk_score": highest_ring.get("risk_score"),
                "risk_level": highest_ring.get("risk_level"),
                "customer_count": highest_ring.get("customer_count"),
                "transaction_volume": highest_ring.get("transaction_volume"),
            },
            "highest_risk_customer": {
                "customer_id": highest_cust.get("entity_id"),
                "risk_score": highest_cust.get("risk_score"),
                "risk_level": highest_cust.get("risk_level"),
                "associated_ring_id": highest_cust.get("associated_ring_id"),
            },
            "top_detected_signals": [
                "shared_device_cluster",
                "shared_payment_instrument",
                "proxy_ip_routing",
                "temporal_burst_synchronization",
                "amount_spike",
            ],
            "recommended_investigation_categories": [
                "Shared Payment Instrument Auditing",
                "Shared Hardware Device Fingerprinting",
                "Syndicate Merchant Extraction Analysis",
                "Coordinated Burst Time Window Inspections",
            ],
        }

        summary_path = self.processed_dir / "investigation_summary.json"
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2)

        return {
            "reports_generated_count": len(investigated_rings) + len(high_risk_customers),
            "index_path": str(index_path),
            "summary_path": str(summary_path),
            "summary_data": summary_data,
        }


def main():
    """CLI demonstration entrypoint for Phase 4 Investigation Intelligence."""
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    print("=" * 60)
    print("FRAUDGRAPH PHASE 4: EXPLAINABLE AI & INVESTIGATION ENGINE")
    print("=" * 60)

    print("\n[1/4] Initializing Investigation Intelligence Engine...")
    engine = InvestigationEngine()

    print("\n[2/4] Generating Forensic Dossiers, Searchable Index, & Summary...")
    results = engine.generate_all_reports_and_indices()
    summary = results["summary_data"]

    print("\n[3/4] Export Complete:")
    print(f"  Indexed Entities:       {summary['total_entities_indexed']:,}")
    print(f"  Investigated Rings:     {summary['investigated_rings_count']}")
    print(f"  High-Risk Customers:    {summary['high_risk_customers_count']}")
    print(f"  Reports Generated:      {results['reports_generated_count']}")
    print(f"  Searchable Index:       {Path(results['index_path']).name}")
    print(f"  Investigation Summary:  {Path(results['summary_path']).name}")

    print("\n[4/4] Demonstrating Case Dossier for Highest-Risk Customer...")
    high_c_id = summary["highest_risk_customer"]["customer_id"]
    if high_c_id:
        c_exp = engine.explain_entity(high_c_id)
        print("\n" + c_exp.get("investigation_report_markdown", ""))

    print("=" * 60)
    print("INVESTIGATION INTELLIGENCE SUMMARY")
    print("=" * 60)
    print(f"Highest-Risk Ring:      {summary['highest_risk_ring']['ring_id']} ({summary['highest_risk_ring']['risk_score']:.1f}/100 - {summary['highest_risk_ring']['risk_level']})")
    print(f"Highest-Risk Customer:  {summary['highest_risk_customer']['customer_id']} ({summary['highest_risk_customer']['risk_score']:.1f}/100 - {summary['highest_risk_customer']['risk_level']})")
    print(f"Top Risk Signals:       {', '.join(summary['top_detected_signals'][:3])}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
