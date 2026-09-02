"""Optional Layer 2 Natural-Language Explanation Layer for FraudGraph.

Strictly bounded by Layer 1 deterministic evidence. The LLM receives only structured
JSON evidence and is constrained by system prompts to prevent hallucination.
Falls back seamlessly to deterministic report generation if no API key is present.
"""

import os
import json
from typing import Dict, List, Optional, Any
from backend.explainability.report_generator import ReportGenerator


class LLMExplainer:
    """Optional LLM-assisted investigation narrative generator with strict hallucination guards."""

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.model_name = model_name
        self.client = None

        if self.api_key:
            try:
                # Initialize google-genai or google.generativeai if available
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel(model_name)
            except Exception:
                self.client = None

    @property
    def is_available(self) -> bool:
        """Returns True if LLM client is configured and available."""
        return self.client is not None

    def explain(self, evidence_data: Dict[str, Any]) -> str:
        """Generates a natural-language investigation summary grounded strictly in provided evidence."""
        if not self.is_available:
            # Deterministic fallback
            entity_type = evidence_data.get("entity_type", "customer")
            if entity_type == "fraud_ring":
                return ReportGenerator.generate_ring_report(evidence_data)
            return ReportGenerator.generate_customer_report(evidence_data)

        # Build grounded prompt
        system_constraints = (
            "You are FraudGraph's Forensic AI Assistant. Your job is to summarize structured fraud evidence.\n"
            "CRITICAL SAFETY RULES:\n"
            "1. You must NEVER invent transactions, accounts, devices, amounts, or fraud rings.\n"
            "2. Cite ONLY the numbers, entities, and evidence items provided in the JSON input.\n"
            "3. Do NOT claim absolute certainty of guilt; use neutral investigative language (e.g. 'evidence suggests', 'recommended review').\n"
            "4. Structure your response clearly: Executive Summary, Evidence Breakdown, and Next Steps.\n"
        )

        user_content = f"Structured Evidence JSON:\n```json\n{json.dumps(evidence_data, indent=2)}\n```\n\nGenerate an investigative summary based ONLY on the evidence above."

        try:
            response = self.client.generate_content(
                f"{system_constraints}\n\n{user_content}",
                generation_config={"temperature": 0.1},
            )
            return response.text.strip()
        except Exception:
            # Graceful fallback on API failure
            return ReportGenerator.generate_customer_report(evidence_data)
