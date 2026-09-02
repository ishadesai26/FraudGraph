"""Deterministic Layer 1 Evidence Engine for FraudGraph.

The authoritative source of truth: constructs structured, quantitative forensic
evidence by corroborating Phase 1 raw data, Phase 2 graph relationships, and
Phase 3 machine learning risk scores without hallucination.
"""

from typing import Dict, List, Optional, Any, Union
import numpy as np
import pandas as pd
import networkx as nx

from backend.explainability.feature_explanations import FeatureExplainer
from backend.explainability.network_explanations import NetworkExplainer
from backend.ml.risk_scorer import CompositeRiskScorer


class EvidenceEngine:
    """Layer 1 deterministic evidence synthesizer for customers, transactions, and fraud rings."""

    def __init__(
        self,
        datasets: Dict[str, pd.DataFrame],
        H: Optional[nx.MultiDiGraph] = None,
        G_cust: Optional[nx.Graph] = None,
        graph_features_df: Optional[pd.DataFrame] = None,
        rings_df: Optional[pd.DataFrame] = None,
        members_df: Optional[pd.DataFrame] = None,
        feature_importance_data: Optional[Dict[str, Any]] = None,
        risk_scorer: Optional[CompositeRiskScorer] = None,
    ):
        self.datasets = datasets
        self.H = H
        self.G_cust = G_cust
        self.graph_features_df = graph_features_df if graph_features_df is not None else pd.DataFrame()
        self.rings_df = rings_df if rings_df is not None else pd.DataFrame()
        self.members_df = members_df if members_df is not None else pd.DataFrame()
        self.risk_scorer = risk_scorer or CompositeRiskScorer()

        self.feature_explainer = FeatureExplainer(feature_importance_data=feature_importance_data)
        self.network_explainer = NetworkExplainer(
            H=H,
            G_cust=G_cust,
            datasets=datasets,
            graph_features_df=graph_features_df,
            rings_df=rings_df,
            members_df=members_df,
        )

        # Index lookups
        self._txns_df = self.datasets.get("transactions", pd.DataFrame())
        self._cust_df = self.datasets.get("customers", pd.DataFrame())

    def calculate_explanation_confidence(
        self,
        risk_signals: List[Dict[str, Any]],
        network_signals: List[Dict[str, Any]],
        has_model_prob: bool = True,
    ) -> str:
        """Determines explanation confidence (HIGH, MEDIUM, LOW) based on multi-source evidence breadth."""
        total_signals = len(risk_signals) + len(network_signals)
        has_network = len(network_signals) > 0
        has_behavioral = len(risk_signals) > 0

        # Multi-layer corroboration across ML, Behavioral, and Graph
        if has_network and has_behavioral and total_signals >= 3:
            return "HIGH"
        elif total_signals >= 2 or (has_network and total_signals >= 1):
            return "MEDIUM"
        else:
            return "LOW"

    def explain_customer(
        self,
        customer_id: str,
        model_prob: Optional[float] = None,
        anomaly_score: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Produces Layer 1 structured evidence dossier for a specific customer."""
        # Find customer transactions
        c_txns = self._txns_df[self._txns_df["customer_id"] == customer_id]
        if c_txns.empty:
            return {"entity_id": customer_id, "entity_type": "customer", "error": f"Customer {customer_id} not found."}

        # Customer demographics
        c_meta = self._cust_df[self._cust_df["customer_id"] == customer_id]
        cust_row = c_meta.iloc[0] if not c_meta.empty else pd.Series()

        # Network explanation
        net_summary = self.network_explainer.explain_customer_network(customer_id)
        net_risk = net_summary.get("network_risk_score", 0.0)

        # Feature explanation (aggregated over latest transaction)
        latest_txn = c_txns.sort_values(by="timestamp").iloc[-1]
        feat_summary = self.feature_explainer.explain_transaction_features(
            txn_row=latest_txn,
            cust_row=cust_row,
            anomaly_score=anomaly_score,
            model_prob=model_prob,
        )

        # Calculate composite risk score
        m_prob = model_prob if model_prob is not None else 0.50
        a_score = anomaly_score if anomaly_score is not None else 50.0
        scored = self.risk_scorer.score_single_event(
            model_prob=m_prob,
            network_risk=net_risk,
            anomaly_score=a_score,
        )

        # Combine all evidence items
        all_evidence = []
        for n_ev in net_summary.get("network_evidence", []):
            all_evidence.append({
                "source": "GRAPH_NETWORK",
                "signal": n_ev.get("signal"),
                "severity": n_ev.get("severity", "MEDIUM"),
                "description": n_ev.get("description"),
            })

        for r_ev in feat_summary.get("risk_signals", []):
            all_evidence.append({
                "source": "BEHAVIORAL_MODEL",
                "signal": r_ev.get("signal"),
                "severity": r_ev.get("severity", "MEDIUM"),
                "description": r_ev.get("description"),
            })

        confidence = self.calculate_explanation_confidence(
            risk_signals=feat_summary.get("risk_signals", []),
            network_signals=net_summary.get("network_evidence", []),
        )

        return {
            "entity_id": customer_id,
            "entity_type": "customer",
            "risk_score": scored["risk_score"],
            "risk_level": scored["risk_level"],
            "explanation_confidence": confidence,
            "associated_ring_id": net_summary.get("ring_id"),
            "member_role": net_summary.get("member_role"),
            "total_transactions": len(c_txns),
            "total_spend": round(float(c_txns["amount"].sum()), 2),
            "evidence": all_evidence,
            "protective_factors": feat_summary.get("protective_signals", []),
            "network_details": net_summary,
            "contributing_signals": scored["signals"],
        }

    def explain_transaction(
        self,
        transaction_id: str,
        model_prob: Optional[float] = None,
        anomaly_score: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Produces Layer 1 structured evidence for an individual transaction."""
        t_match = self._txns_df[self._txns_df["transaction_id"] == transaction_id]
        if t_match.empty:
            return {"entity_id": transaction_id, "entity_type": "transaction", "error": f"Transaction {transaction_id} not found."}

        txn_row = t_match.iloc[0]
        cust_id = str(txn_row["customer_id"])

        # Customer & network context
        cust_explanation = self.explain_customer(
            customer_id=cust_id,
            model_prob=model_prob,
            anomaly_score=anomaly_score,
        )

        return {
            "entity_id": transaction_id,
            "entity_type": "transaction",
            "customer_id": cust_id,
            "amount": float(txn_row["amount"]),
            "timestamp": str(txn_row["timestamp"]),
            "payment_type": txn_row.get("payment_type"),
            "merchant_id": txn_row.get("merchant_id"),
            "risk_score": cust_explanation["risk_score"],
            "risk_level": cust_explanation["risk_level"],
            "explanation_confidence": cust_explanation["explanation_confidence"],
            "associated_ring_id": cust_explanation.get("associated_ring_id"),
            "evidence": cust_explanation["evidence"],
            "protective_factors": cust_explanation.get("protective_factors", []),
            "contributing_signals": cust_explanation.get("contributing_signals", []),
        }

    def explain_fraud_ring(self, ring_id: str) -> Dict[str, Any]:
        """Produces Layer 1 structured evidence dossier for a fraud ring syndicate."""
        ring_summary = self.network_explainer.explain_fraud_ring(ring_id)
        if "error" in ring_summary:
            return ring_summary

        dev_cnt = int(ring_summary.get("shared_devices_count", ring_summary.get("shared_device_count", 0)))
        pm_cnt = int(ring_summary.get("shared_payments_count", ring_summary.get("shared_payment_count", 0)))
        confidence = "HIGH" if dev_cnt > 0 and pm_cnt > 0 else "MEDIUM"

        return {
            "entity_id": ring_id,
            "entity_type": "fraud_ring",
            "risk_score": float(ring_summary.get("risk_score", 0.0)),
            "risk_level": ring_summary.get("risk_level", "HIGH"),
            "explanation_confidence": confidence,
            "customer_count": int(ring_summary.get("customer_count", 0)),
            "transaction_count": int(ring_summary.get("transaction_count", 0)),
            "transaction_volume": float(ring_summary.get("transaction_volume", 0.0)),
            "shared_devices_count": dev_cnt,
            "shared_payments_count": pm_cnt,
            "evidence": ring_summary.get("evidence", []),
            "top_members": ring_summary.get("top_members", ring_summary.get("members", [])),
        }
