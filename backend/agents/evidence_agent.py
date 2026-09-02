"""Agent 4: Evidence Agent — Aggregates, ranks, detects conflicts, and computes evidence coverage."""

from typing import Dict, Any, List, Set
from backend.agents.base_agent import BaseAgent
from backend.agents.schemas import AgentEvidenceItem, ConflictItem


class EvidenceAgent(BaseAgent):
    """Specialized agent synthesizing multi-agent evidence, detecting conflicts, and measuring coverage."""

    def __init__(self):
        super().__init__(
            name="EvidenceAgent",
            description="Aggregates and ranks evidence from Risk, Graph, and Behavior agents; detects conflicts; computes coverage.",
        )

    def _execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        risk_out = context.get("risk_agent_output", {})
        graph_out = context.get("graph_agent_output", {})
        behavior_out = context.get("behavior_agent_output", {})

        raw_evidence: List[AgentEvidenceItem] = []
        raw_evidence.extend(risk_out.get("evidence", []))
        raw_evidence.extend(graph_out.get("evidence", []))
        raw_evidence.extend(behavior_out.get("evidence", []))

        # 1. Deduplicate and rank evidence
        seen_signals: Set[str] = set()
        deduped_evidence: List[AgentEvidenceItem] = []
        severity_rank = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}

        for item in raw_evidence:
            if item.signal not in seen_signals:
                seen_signals.add(item.signal)
                deduped_evidence.append(item)

        # Sort: CRITICAL -> HIGH -> MEDIUM -> LOW, then by importance
        deduped_evidence.sort(
            key=lambda x: (severity_rank.get(x.severity, 0), x.importance or 0.0),
            reverse=True,
        )

        # 2. Conflict Detection
        conflicts: List[ConflictItem] = []
        
        ml_level = risk_out.get("ml_risk_level", "LOW")
        net_level = graph_out.get("network_risk_level", "LOW")
        beh_level = behavior_out.get("behavior_risk_level", "LOW")
        
        ml_score = risk_out.get("ml_risk_score", 0.0)
        net_score = graph_out.get("network_risk_score", 0.0)

        # Conflict 1: Model High vs Network Clean
        if (ml_score >= 75.0 or ml_level in ["HIGH", "CRITICAL"]) and (net_score < 35.0 and graph_out.get("shared_devices_count", 0) == 0):
            conflicts.append(
                ConflictItem(
                    type="model_network_discrepancy",
                    description="Supervised behavioral model indicates high risk, while graph network topology reveals no shared hardware or syndicate ties.",
                    supporting_signals=["supervised_ml_high_confidence_fraud"],
                    opposing_signals=["isolated_graph_topology"],
                )
            )
        # Conflict 2: Network Syndicate High vs Model Clean
        elif (net_score >= 75.0 or net_level in ["HIGH", "CRITICAL"]) and (ml_score < 35.0):
            conflicts.append(
                ConflictItem(
                    type="network_model_discrepancy",
                    description="Graph network topology indicates strong syndicate/shared-resource clustering, but individual transaction features appear benign.",
                    supporting_signals=["syndicate_ring_membership", "shared_device_hardware_cluster"],
                    opposing_signals=["supervised_ml_clean_baseline"],
                )
            )

        # Conflict 3: Burst Velocity on Established KYC Account
        if behavior_out.get("burst_count", 0) >= 2 and any(e.signal == "established_account_tenure" for e in deduped_evidence):
            conflicts.append(
                ConflictItem(
                    type="velocity_tenure_tension",
                    description="Account exhibits high-velocity burst transactions despite having established tenure and verified KYC identity.",
                    supporting_signals=["temporal_burst_synchronization"],
                    opposing_signals=["established_account_tenure", "kyc_verification_complete"],
                )
            )

        # 3. Calculate Evidence Coverage Score (0.0 to 100.0%)
        # Explicitly evaluates data completeness & cross-agent corroboration
        coverage_points = 0.0
        if "ml_risk_score" in risk_out:
            coverage_points += 25.0
        if "network_risk_score" in graph_out:
            coverage_points += 25.0
        if "total_transactions" in behavior_out:
            coverage_points += 25.0

        # Corroboration bonus if >= 2 independent agents found signals
        active_agents = set([e.source_agent for e in deduped_evidence if e.severity in ["HIGH", "CRITICAL"]])
        if len(active_agents) >= 2:
            coverage_points += 25.0
        elif len(deduped_evidence) > 0:
            coverage_points += 15.0

        evidence_coverage = min(100.0, round(coverage_points, 1))

        summary = (
            f"EvidenceAgent correlated {len(deduped_evidence)} signals across 3 agents "
            f"(Coverage: {evidence_coverage}%, {len(conflicts)} conflict(s) detected)."
        )

        return {
            "evidence": deduped_evidence,
            "conflicts": conflicts,
            "evidence_coverage": evidence_coverage,
            "corroborated_sources": list(active_agents),
            "summary": summary,
        }
