"""Multi-Agent Orchestrator for Phase 6 Agentic Fraud Investigation."""

import os
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

from backend.agents.schemas import (
    AgentInvestigationResult,
    AgentTraceStep,
    DecisionResult,
)
from backend.agents.risk_agent import RiskAgent
from backend.agents.graph_agent import GraphAgent
from backend.agents.behavior_agent import BehaviorAgent
from backend.agents.evidence_agent import EvidenceAgent
from backend.agents.investigator_agent import InvestigatorAgent
from backend.agents.decision_agent import DecisionAgent
from backend.agents.evidence_graph import EvidenceGraphBuilder
from backend.agents.llm_synthesizer import LLMSynthesizer


class AgentOrchestrator:
    """Orchestrates 6 specialized agents to perform collaborative fraud investigation."""

    def __init__(self, investigations_dir: Optional[str] = None):
        self.risk_agent = RiskAgent()
        self.graph_agent = GraphAgent()
        self.behavior_agent = BehaviorAgent()
        self.evidence_agent = EvidenceAgent()
        self.investigator_agent = InvestigatorAgent()
        self.decision_agent = DecisionAgent()
        self.llm_synthesizer = LLMSynthesizer()

        base_dir = Path(__file__).resolve().parent.parent.parent
        self.investigations_dir = Path(investigations_dir) if investigations_dir else (base_dir / "data" / "processed" / "agent_investigations")
        self.investigations_dir.mkdir(parents=True, exist_ok=True)

    def investigate(
        self,
        entity_type: str,
        entity_id: str,
        risk_data: Optional[Dict[str, Any]] = None,
        graph_data: Optional[Dict[str, Any]] = None,
        behavior_data: Optional[Dict[str, Any]] = None,
        timeline: Optional[List[Dict[str, Any]]] = None,
    ) -> AgentInvestigationResult:
        """Executes the full 6-agent collaborative investigation pipeline."""
        risk_data = risk_data or {}
        graph_data = graph_data or {}
        behavior_data = behavior_data or {}
        timeline = timeline or []

        trace_steps: List[AgentTraceStep] = []
        context: Dict[str, Any] = {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "risk_data": risk_data,
            "graph_data": graph_data,
            "behavior_data": behavior_data,
            "timeline": timeline,
        }

        # Step 1: Run Risk Agent
        risk_out = self.risk_agent.run(context)
        trace_steps.append(risk_out["trace_step"])
        context["risk_agent_output"] = risk_out

        # Step 2: Run Graph Agent
        graph_out = self.graph_agent.run(context)
        trace_steps.append(graph_out["trace_step"])
        context["graph_agent_output"] = graph_out

        # Step 3: Run Behavior Agent
        behavior_out = self.behavior_agent.run(context)
        trace_steps.append(behavior_out["trace_step"])
        context["behavior_agent_output"] = behavior_out

        # Step 4: Run Evidence Agent (Aggregator & Conflict Detector)
        evidence_out = self.evidence_agent.run(context)
        trace_steps.append(evidence_out["trace_step"])
        context["evidence_agent_output"] = evidence_out

        # Step 5: Run Investigator Agent (Forensic Synthesizer)
        investigator_out = self.investigator_agent.run(context)
        trace_steps.append(investigator_out["trace_step"])
        context["investigator_agent_output"] = investigator_out

        # Step 6: Run Decision Agent (Final Verdict)
        decision_out = self.decision_agent.run(context)
        trace_steps.append(decision_out["trace_step"])
        decision: DecisionResult = decision_out["decision"]

        # Step 7: Build Structured Evidence Graph
        evidence_items = evidence_out.get("evidence", [])
        evidence_graph = EvidenceGraphBuilder.build(
            entity_type=entity_type,
            entity_id=entity_id,
            evidence_items=evidence_items,
            graph_data=graph_data,
            decision_status=decision.status,
        )

        # Step 8: Generate Narrative
        conflicts = evidence_out.get("conflicts", [])
        key_findings = investigator_out.get("key_findings", [])
        narrative = self.llm_synthesizer.synthesize(
            entity_type=entity_type,
            entity_id=entity_id,
            decision=decision,
            key_findings=key_findings,
            evidence_items=evidence_items,
            conflicts=conflicts,
        )

        investigation_id = f"INV_{entity_type.upper()}_{entity_id.replace(':', '_')}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        result = AgentInvestigationResult(
            investigation_id=investigation_id,
            timestamp=timestamp,
            entity_type=entity_type,
            entity_id=entity_id,
            risk_score=decision.risk_score,
            risk_level=decision.status,
            decision=decision,
            key_findings=key_findings,
            evidence_items=evidence_items,
            conflicts=conflicts,
            entities_to_review=investigator_out.get("entities_to_review", []),
            network_context={
                "network_risk_score": graph_out.get("network_risk_score", 0.0),
                "ring_id": graph_out.get("ring_id"),
                "shared_devices_count": graph_out.get("shared_devices_count", 0),
                "shared_payments_count": graph_out.get("shared_payments_count", 0),
            },
            behavior_context={
                "behavior_risk_level": behavior_out.get("behavior_risk_level", "LOW"),
                "burst_count": behavior_out.get("burst_count", 0),
                "total_transactions": behavior_out.get("total_transactions", 0),
                "total_spend": behavior_out.get("total_spend", 0.0),
            },
            evidence_graph=evidence_graph,
            agent_trace=trace_steps,
            narrative_summary=narrative,
        )

        # Step 9: Persist Completed Investigation
        self._save_investigation(result)

        return result

    def _save_investigation(self, result: AgentInvestigationResult):
        """Persist investigation result as a JSON artifact."""
        filepath = self.investigations_dir / f"{result.investigation_id}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(result.model_dump(), f, indent=2)

    def load_investigation(self, investigation_id: str) -> Optional[AgentInvestigationResult]:
        """Load a previously executed investigation from disk."""
        filepath = self.investigations_dir / f"{investigation_id}.json"
        if not filepath.exists():
            return None
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return AgentInvestigationResult(**data)
