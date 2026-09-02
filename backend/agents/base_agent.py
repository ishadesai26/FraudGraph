"""Base agent class for FraudGraph Phase 6 multi-agent orchestration."""

import abc
import time
from typing import Dict, Any, List, Optional
from backend.agents.schemas import AgentTraceStep, AgentEvidenceItem


class BaseAgent(abc.ABC):
    """Abstract Base Agent with standardized execution envelope and trace recording."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent with automatic execution timing and error-safe trace recording."""
        start_time = time.perf_counter()
        status = "completed"
        summary = ""
        evidence_items: List[AgentEvidenceItem] = []
        result_payload: Dict[str, Any] = {}

        try:
            result_payload = self._execute(context)
            evidence_items = result_payload.get("evidence", [])
            summary = result_payload.get("summary", f"{self.name} completed evaluation.")
        except Exception as exc:
            status = "failed"
            summary = f"{self.name} encountered an error: {str(exc)}"
            result_payload = {"error": str(exc), "evidence": []}

        duration_ms = (time.perf_counter() - start_time) * 1000.0

        trace_step = AgentTraceStep(
            agent_name=self.name,
            status=status,
            duration_ms=round(duration_ms, 2),
            signals_found=len(evidence_items),
            summary=summary,
        )

        return {
            **result_payload,
            "trace_step": trace_step,
            "evidence": evidence_items,
        }

    @abc.abstractmethod
    def _execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Core specialized agent logic to be implemented by child classes."""
        raise NotImplementedError

    def create_evidence(
        self,
        signal: str,
        description: str,
        severity: str = "MEDIUM",
        value: Optional[Any] = None,
        importance: Optional[float] = None,
        category: str = "GENERAL",
    ) -> AgentEvidenceItem:
        """Helper to create evidence items with strict source agent provenance."""
        return AgentEvidenceItem(
            signal=signal,
            source_agent=self.name,
            severity=severity,
            value=value,
            importance=importance,
            description=description,
            category=category,
        )
