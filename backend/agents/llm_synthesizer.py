"""Optional LLM Synthesis layer with deterministic template fallback."""

import os
from typing import Dict, Any, List
from backend.agents.schemas import AgentEvidenceItem, DecisionResult


class LLMSynthesizer:
    """Generates natural-language investigation narratives using Gemini API or deterministic fallback."""

    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

    def synthesize(
        self,
        entity_type: str,
        entity_id: str,
        decision: DecisionResult,
        key_findings: List[str],
        evidence_items: List[AgentEvidenceItem],
        conflicts: List[Any],
    ) -> str:
        """Synthesize a cohesive investigative executive summary."""
        # Check if LLM API is available
        if self.api_key:
            try:
                return self._call_llm(entity_type, entity_id, decision, key_findings, evidence_items, conflicts)
            except Exception:
                pass  # Graceful fallback to deterministic template

        return self._deterministic_template(entity_type, entity_id, decision, key_findings, evidence_items, conflicts)

    def _deterministic_template(
        self,
        entity_type: str,
        entity_id: str,
        decision: DecisionResult,
        key_findings: List[str],
        evidence_items: List[AgentEvidenceItem],
        conflicts: List[Any],
    ) -> str:
        """Standardized, zero-hallucination deterministic narrative."""
        findings_text = "\n".join([f"- {f}" for f in key_findings]) if key_findings else "- No anomalous signals identified."
        conflict_text = f"\n*Note: {len(conflicts)} inter-agent conflict(s) were flagged for analyst adjudication.*" if conflicts else ""

        narrative = (
            f"### Multi-Agent Forensic Investigation Summary for {entity_type.title()} {entity_id}\n\n"
            f"**Final Disposition:** {decision.status} (Composite Risk: {decision.risk_score:.1f}/100, "
            f"Confidence: {decision.confidence}, Evidence Coverage: {decision.evidence_coverage:.1f}%)\n\n"
            f"**Executive Reasoning:**\n{decision.reasoning}\n\n"
            f"**Key Investigative Findings:**\n{findings_text}\n"
            f"{conflict_text}\n\n"
            f"**Recommended Action:**\n{decision.recommended_action}"
        )
        return narrative

    def _call_llm(
        self,
        entity_type: str,
        entity_id: str,
        decision: DecisionResult,
        key_findings: List[str],
        evidence_items: List[AgentEvidenceItem],
        conflicts: List[Any],
    ) -> str:
        """Call google-genai SDK when available."""
        from google import genai
        client = genai.Client(api_key=self.api_key)
        
        prompt = (
            f"You are a neutral, objective fintech fraud investigation assistant. "
            f"Write a concise executive summary based strictly on these verified multi-agent findings. "
            f"Do not invent new facts, transaction amounts, or accusations.\n\n"
            f"Entity: {entity_type} {entity_id}\n"
            f"Decision: {decision.status} (Risk Score: {decision.risk_score})\n"
            f"Confidence: {decision.confidence}, Coverage: {decision.evidence_coverage}%\n"
            f"Reasoning: {decision.reasoning}\n"
            f"Key Findings: {key_findings}\n"
            f"Conflicts: {[c.description for c in conflicts]}\n"
            f"Recommended Action: {decision.recommended_action}"
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text
