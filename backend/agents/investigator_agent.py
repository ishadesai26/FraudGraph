"""Agent 5: Investigator Agent — Formulates investigative findings, hypotheses, and forensic checks."""

from typing import Dict, Any, List
from backend.agents.base_agent import BaseAgent
from backend.agents.schemas import AgentEvidenceItem


class InvestigatorAgent(BaseAgent):
    """Specialized agent framing objective forensic findings, review targets, and investigative checks."""

    def __init__(self):
        super().__init__(
            name="InvestigatorAgent",
            description="Acts as the lead fraud investigator: synthesizes key findings, identifies linked entities to audit, and recommends checks.",
        )

    def _execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        evidence_out = context.get("evidence_agent_output", {})
        evidence_items: List[AgentEvidenceItem] = evidence_out.get("evidence", [])
        conflicts = evidence_out.get("conflicts", [])
        graph_data = context.get("graph_data", {})
        entity_id = context.get("entity_id", "UNKNOWN")
        entity_type = context.get("entity_type", "customer")

        # 1. Synthesize Key Findings from ranked evidence
        key_findings: List[str] = []
        critical_high_items = [e for e in evidence_items if e.severity in ["CRITICAL", "HIGH"]]

        if critical_high_items:
            for item in critical_high_items[:4]:
                key_findings.append(f"{item.signal.replace('_', ' ').title()}: {item.description}")
        else:
            key_findings.append("No critical or high-severity risk signals identified across behavioral or network profiles.")

        # 2. Identify Connected Entities Requiring Forensic Review
        entities_to_review: List[Dict[str, Any]] = []
        
        # Shared Devices
        for dev in graph_data.get("shared_devices", [])[:3]:
            entities_to_review.append({
                "entity_id": dev.get("resource_id", "DEV_UNKNOWN"),
                "type": "device",
                "reason": f"Hardware shared with {dev.get('shared_with_count', 0)} other accounts.",
                "priority": "HIGH" if dev.get("shared_with_count", 0) >= 3 else "MEDIUM",
            })

        # Shared Payments
        for pm in graph_data.get("shared_payments", [])[:3]:
            entities_to_review.append({
                "entity_id": pm.get("resource_id", "PM_UNKNOWN"),
                "type": "payment_method",
                "reason": f"Payment instrument shared with {pm.get('shared_with_count', 0)} accounts.",
                "priority": "HIGH" if pm.get("shared_with_count", 0) >= 2 else "MEDIUM",
            })

        # Connected Customers
        for neighbor in graph_data.get("connected_neighbors", [])[:3]:
            entities_to_review.append({
                "entity_id": neighbor.get("customer_id", "CUST_UNKNOWN"),
                "type": "customer",
                "reason": f"Co-transacting or shared infrastructure neighbor ({neighbor.get('common_resource', 'shared linkage')}).",
                "priority": "MEDIUM",
            })

        # 3. Recommended Forensic Checks (Neutral investigative language)
        recommended_checks: List[str] = []
        if any(e.signal == "syndicate_ring_membership" for e in evidence_items):
            ring_id = graph_data.get("associated_ring_id", "Syndicate")
            recommended_checks.append(f"Conduct comprehensive cross-account ledger audit across all accounts associated with syndicate '{ring_id}'.")
        
        if any(e.signal == "shared_device_hardware_cluster" for e in evidence_items):
            recommended_checks.append("Verify device fingerprint integrity and inspect telemetry for emulator or bot automation signatures.")

        if any(e.signal == "shared_payment_instrument_collusion" for e in evidence_items):
            recommended_checks.append("Reconcile payment instrument holder names against KYC beneficiary records to detect synthetic identity collusion.")

        if any(e.signal == "temporal_burst_synchronization" for e in evidence_items):
            recommended_checks.append("Inspect transaction execution timestamps against gateway ingress logs for scripted API bursts.")

        if not recommended_checks:
            recommended_checks.append("Standard periodic monitoring; maintain normal transaction verification rules.")

        investigation_summary = (
            f"Forensic review of {entity_type} '{entity_id}' identified {len(critical_high_items)} primary risk indicator(s) "
            f"with {len(entities_to_review)} correlated infrastructure/neighbor entity(ies) requiring audit."
        )

        return {
            "key_findings": key_findings,
            "entities_to_review": entities_to_review,
            "recommended_checks": recommended_checks,
            "investigation_summary": investigation_summary,
            "evidence": [],  # Investigator produces findings, not raw evidence
            "summary": f"InvestigatorAgent generated {len(key_findings)} key findings and {len(recommended_checks)} investigative checks.",
        }
