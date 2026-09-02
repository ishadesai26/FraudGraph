"""Agent 6: Decision Agent — Produces final investigation disposition, confidence, and actions."""

from typing import Dict, Any, List
from backend.agents.base_agent import BaseAgent
from backend.agents.schemas import DecisionResult, AgentEvidenceItem


class DecisionAgent(BaseAgent):
    """Specialized agent synthesizing final investigation verdict, confidence level, and actionable recommendations."""

    def __init__(self):
        super().__init__(
            name="DecisionAgent",
            description="Synthesizes final risk verdict (LOW_RISK, REVIEW, ENHANCED_REVIEW, HIGH_RISK), confidence, and action plan.",
        )

    def _execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        risk_data = context.get("risk_data", {})
        risk_score = float(risk_data.get("risk_score", 0.0))
        
        evidence_out = context.get("evidence_agent_output", {})
        evidence_items: List[AgentEvidenceItem] = evidence_out.get("evidence", [])
        conflicts = evidence_out.get("conflicts", [])
        evidence_coverage = float(evidence_out.get("evidence_coverage", 50.0))
        
        investigator_out = context.get("investigator_agent_output", {})
        recommended_checks = investigator_out.get("recommended_checks", [])

        # Count signal severities
        critical_count = sum(1 for e in evidence_items if e.severity == "CRITICAL")
        high_count = sum(1 for e in evidence_items if e.severity == "HIGH")
        medium_count = sum(1 for e in evidence_items if e.severity == "MEDIUM")

        # 1. Determine Final Disposition Status
        if risk_score >= 80.0 or critical_count >= 1 or high_count >= 3:
            status = "HIGH_RISK"
            primary_action = "Initiate immediate transaction hold and escalate for senior fraud operations review."
        elif risk_score >= 60.0 or high_count >= 1:
            status = "ENHANCED_REVIEW"
            primary_action = "Apply step-up identity authentication and place account under temporary 48-hour velocity monitoring."
        elif risk_score >= 35.0 or len(conflicts) > 0 or medium_count >= 2:
            status = "REVIEW"
            primary_action = "Queue for routine manual analyst review within standard SLA window."
        else:
            status = "LOW_RISK"
            primary_action = "No intervention required; permit standard transaction processing."

        # 2. Determine Confidence Level (distinct from fraud probability)
        # Confidence reflects data completeness, multi-agent agreement, and absence of severe conflicts
        if evidence_coverage >= 75.0 and len(conflicts) == 0 and (critical_count + high_count >= 2 or risk_score < 25.0):
            confidence = "HIGH"
        elif evidence_coverage >= 50.0 and len(conflicts) <= 1:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"

        # 3. Formulate Reasoning Narrative
        if status == "HIGH_RISK":
            reasoning = (
                f"Multi-agent consensus established severe fraud risk (Score: {risk_score:.1f}/100). "
                f"Corroborated by {critical_count} critical and {high_count} high-severity signal(s) across ML models and graph linkages."
            )
        elif status == "ENHANCED_REVIEW":
            reasoning = (
                f"Elevated risk indicators detected (Score: {risk_score:.1f}/100). "
                f"Supported by {high_count} high-severity finding(s), warranting proactive step-up verification."
            )
        elif status == "REVIEW":
            if conflicts:
                reasoning = (
                    f"Moderate risk (Score: {risk_score:.1f}/100) with {len(conflicts)} active inter-agent disagreement(s) "
                    "requiring manual analyst adjudication."
                )
            else:
                reasoning = f"Moderate risk indicators observed (Score: {risk_score:.1f}/100); recommended for routine analyst inspection."
        else:
            reasoning = (
                f"Low composite risk (Score: {risk_score:.1f}/100) with clean behavioral baseline and no coordinated graph collusion."
            )

        decision = DecisionResult(
            status=status,
            risk_score=round(risk_score, 1),
            confidence=confidence,
            evidence_coverage=evidence_coverage,
            reasoning=reasoning,
            recommended_action=primary_action,
            recommended_actions=[primary_action] + recommended_checks[:3],
        )

        return {
            "decision": decision,
            "evidence": [],
            "summary": f"DecisionAgent ruled {status} (Risk: {risk_score:.1f}, Confidence: {confidence}, Coverage: {evidence_coverage}%).",
        }
