"""Agent 1: Risk Agent — Evaluates ML model outputs and anomaly scores."""

from typing import Dict, Any, List
from backend.agents.base_agent import BaseAgent
from backend.agents.schemas import AgentEvidenceItem


class RiskAgent(BaseAgent):
    """Specialized agent evaluating supervised ML probabilities and unsupervised anomaly scores."""

    def __init__(self):
        super().__init__(
            name="RiskAgent",
            description="Analyzes Phase 3 supervised RandomForest probabilities, IsolationForest anomaly scores, and ML uplift.",
        )

    def _execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        evidence: List[AgentEvidenceItem] = []
        entity_type = context.get("entity_type", "customer")
        risk_data = context.get("risk_data", {})
        
        # Extract ML metrics
        risk_score = float(risk_data.get("risk_score", 0.0))
        supervised_prob = float(risk_data.get("supervised_model_probability", risk_data.get("supervised_prob", 0.0)))
        anomaly_score = float(risk_data.get("unsupervised_anomaly_score", risk_data.get("anomaly_score", 0.0)))
        baseline_prob = float(risk_data.get("baseline_probability", risk_data.get("baseline_prob", supervised_prob)))
        graph_prob = float(risk_data.get("graph_model_probability", risk_data.get("graph_prob", supervised_prob)))

        # 1. Supervised Model Risk Evaluation
        if supervised_prob >= 0.80 or risk_score >= 80.0:
            evidence.append(
                self.create_evidence(
                    signal="supervised_ml_high_confidence_fraud",
                    description=f"Graph-enhanced RandomForest fraud classifier estimated a {supervised_prob:.1%} fraud probability.",
                    severity="CRITICAL" if supervised_prob >= 0.90 else "HIGH",
                    value=round(supervised_prob, 4),
                    importance=0.45,
                    category="ML_MODEL",
                )
            )
        elif supervised_prob >= 0.40 or risk_score >= 50.0:
            evidence.append(
                self.create_evidence(
                    signal="supervised_ml_moderate_risk",
                    description=f"Supervised model indicates elevated fraud probability of {supervised_prob:.1%}.",
                    severity="MEDIUM",
                    value=round(supervised_prob, 4),
                    importance=0.30,
                    category="ML_MODEL",
                )
            )
        elif supervised_prob < 0.15 and risk_score < 30.0:
            evidence.append(
                self.create_evidence(
                    signal="supervised_ml_clean_baseline",
                    description=f"Supervised model assigned a low fraud probability of {supervised_prob:.1%}.",
                    severity="LOW",
                    value=round(supervised_prob, 4),
                    importance=0.20,
                    category="PROTECTIVE",
                )
            )

        # 2. Unsupervised Outlier Anomaly Detection
        if anomaly_score >= 80.0:
            evidence.append(
                self.create_evidence(
                    signal="unsupervised_isolation_anomaly",
                    description=f"IsolationForest identified severe multidimensional behavioral anomaly (Score: {anomaly_score:.1f}/100).",
                    severity="HIGH",
                    value=round(anomaly_score, 1),
                    importance=0.35,
                    category="ML_MODEL",
                )
            )
        elif anomaly_score >= 50.0:
            evidence.append(
                self.create_evidence(
                    signal="unsupervised_moderate_deviation",
                    description=f"Unsupervised anomaly detector noted moderate deviation (Score: {anomaly_score:.1f}/100).",
                    severity="MEDIUM",
                    value=round(anomaly_score, 1),
                    importance=0.20,
                    category="ML_MODEL",
                )
            )

        # 3. Graph-vs-Baseline Model Uplift Evaluation
        prob_uplift = graph_prob - baseline_prob
        if prob_uplift >= 0.20:
            evidence.append(
                self.create_evidence(
                    signal="network_feature_model_uplift",
                    description=f"Network topology features elevated fraud probability by +{prob_uplift:.1%} above isolated behavioral baseline.",
                    severity="HIGH",
                    value=round(prob_uplift, 4),
                    importance=0.25,
                    category="ML_MODEL",
                )
            )

        # Determine ML Assessment
        ml_level = "LOW"
        if risk_score >= 80.0 or supervised_prob >= 0.80:
            ml_level = "CRITICAL" if risk_score >= 90.0 else "HIGH"
        elif risk_score >= 50.0 or supervised_prob >= 0.40:
            ml_level = "MEDIUM"

        summary = f"RiskAgent evaluated ML models: Composite Score {risk_score:.1f} ({ml_level}), Supervised Prob {supervised_prob:.1%}, Anomaly Score {anomaly_score:.1f}."

        return {
            "ml_risk_score": risk_score,
            "ml_risk_level": ml_level,
            "supervised_probability": supervised_prob,
            "anomaly_score": anomaly_score,
            "evidence": evidence,
            "summary": summary,
        }
