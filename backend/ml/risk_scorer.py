"""Composite risk scoring and signal attribution engine for FraudGraph.

Combines supervised model probabilities, unsupervised anomaly scores, and graph
network risk into a normalized 0-100 score with risk levels and structured signals.
"""

from typing import Dict, List, Optional, Any, Union
import numpy as np
import pandas as pd


class CompositeRiskScorer:
    """Calculates multi-factor composite risk scores and structured signal attributions."""

    WEIGHT_MODEL_PROB: float = 0.50
    WEIGHT_NETWORK_RISK: float = 0.25
    WEIGHT_ANOMALY_SCORE: float = 0.25

    def __init__(
        self,
        weight_model: float = 0.50,
        weight_network: float = 0.25,
        weight_anomaly: float = 0.25,
    ):
        total_w = weight_model + weight_network + weight_anomaly
        self.w_model = weight_model / total_w
        self.w_network = weight_network / total_w
        self.w_anomaly = weight_anomaly / total_w

    @staticmethod
    def classify_risk_tier(score: float) -> str:
        """Categorizes continuous 0-100 score into standard risk tier."""
        if score >= 80.0:
            return "CRITICAL"
        elif score >= 60.0:
            return "HIGH"
        elif score >= 35.0:
            return "MEDIUM"
        else:
            return "LOW"

    def score_single_event(
        self,
        model_prob: float,
        network_risk: float,
        anomaly_score: float,
        raw_feature_dict: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Scores a single transaction event and produces structured explainability signals."""
        model_component = np.clip(model_prob * 100.0, 0.0, 100.0)
        network_component = np.clip(network_risk, 0.0, 100.0)
        anomaly_component = np.clip(anomaly_score, 0.0, 100.0)

        composite_score = (
            self.w_model * model_component
            + self.w_network * network_component
            + self.w_anomaly * anomaly_component
        )
        composite_score = round(float(np.clip(composite_score, 0.0, 100.0)), 2)
        risk_level = self.classify_risk_tier(composite_score)

        signals = [
            {
                "name": "supervised_model_probability",
                "value": round(float(model_component), 2),
                "importance": round(self.w_model, 2),
            },
            {
                "name": "network_risk_score",
                "value": round(float(network_component), 2),
                "importance": round(self.w_network, 2),
            },
            {
                "name": "unsupervised_anomaly_score",
                "value": round(float(anomaly_component), 2),
                "importance": round(self.w_anomaly, 2),
            },
        ]

        if raw_feature_dict:
            # Highlight top raw behavioral signals
            if "transaction_velocity_per_day" in raw_feature_dict:
                signals.append({
                    "name": "transaction_velocity_per_day",
                    "value": round(float(raw_feature_dict["transaction_velocity_per_day"]), 2),
                    "importance": 0.15,
                })
            if "amount" in raw_feature_dict:
                signals.append({
                    "name": "transaction_amount",
                    "value": round(float(raw_feature_dict["amount"]), 2),
                    "importance": 0.10,
                })
            if "shared_device_count" in raw_feature_dict and raw_feature_dict["shared_device_count"] > 0:
                signals.append({
                    "name": "shared_device_count",
                    "value": int(raw_feature_dict["shared_device_count"]),
                    "importance": 0.20,
                })

        return {
            "risk_score": composite_score,
            "risk_level": risk_level,
            "signals": signals,
        }

    def score_batch(
        self,
        model_probs: np.ndarray,
        network_risks: np.ndarray,
        anomaly_scores: np.ndarray,
    ) -> pd.DataFrame:
        """Scores an entire batch of transactions efficiently."""
        m_comp = np.clip(np.asarray(model_probs) * 100.0, 0.0, 100.0)
        n_comp = np.clip(np.asarray(network_risks), 0.0, 100.0)
        a_comp = np.clip(np.asarray(anomaly_scores), 0.0, 100.0)

        composite = self.w_model * m_comp + self.w_network * n_comp + self.w_anomaly * a_comp
        composite = np.clip(composite, 0.0, 100.0).round(2)

        tiers = [self.classify_risk_tier(s) for s in composite]

        return pd.DataFrame({
            "model_probability_pct": m_comp.round(2),
            "network_risk_pct": n_comp.round(2),
            "anomaly_score_pct": a_comp.round(2),
            "composite_risk_score": composite,
            "risk_level": tiers,
        })
