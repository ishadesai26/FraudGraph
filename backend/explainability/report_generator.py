"""Deterministic forensic investigation report generator for FraudGraph.

Translates Layer 1 structured evidence dictionaries into formatted, human-readable
investigation dossiers and markdown summaries with zero hallucination.
"""

from typing import Dict, List, Optional, Any


class ReportGenerator:
    """Formats structured Layer 1 evidence into investigation reports."""

    @staticmethod
    def generate_customer_report(evidence_data: Dict[str, Any]) -> str:
        """Generates markdown investigation dossier for a customer."""
        cust_id = evidence_data.get("entity_id", "Unknown")
        risk_score = evidence_data.get("risk_score", 0.0)
        risk_level = evidence_data.get("risk_level", "LOW")
        conf = evidence_data.get("explanation_confidence", "LOW")
        ring_id = evidence_data.get("associated_ring_id") or "None (Isolated Node)"
        role = evidence_data.get("member_role", "MEMBER")
        txns_count = evidence_data.get("total_transactions", 0)
        total_spend = evidence_data.get("total_spend", 0.0)

        lines = [
            "# FRAUDGRAPH FORENSIC INVESTIGATION REPORT",
            "============================================================",
            f"**Target Entity**: Customer `{cust_id}`",
            f"**Composite Risk Score**: `{risk_score:.1f} / 100` ({risk_level})",
            f"**Explanation Confidence**: `{conf}`",
            f"**Syndicate Association**: `{ring_id}` ({role})",
            f"**Transactional History**: {txns_count} transactions (₹{total_spend:,.2f})",
            "------------------------------------------------------------",
            "",
            "## 1. Primary Reasons Flagged",
        ]

        evidence_list = evidence_data.get("evidence", [])
        if evidence_list:
            for idx, ev in enumerate(evidence_list[:5], 1):
                lines.append(f"{idx}. [{ev.get('severity', 'MEDIUM')}] {ev.get('description')}")
        else:
            lines.append("No critical fraud signals detected. Standard account behavior.")

        lines.extend([
            "",
            "## 2. Network & Relational Evidence",
        ])

        net_details = evidence_data.get("network_details", {})
        shared_devs = net_details.get("shared_devices", [])
        shared_pms = net_details.get("shared_payments", [])

        if shared_devs:
            lines.append(f"- **Shared Hardware Devices**: {len(shared_devs)} devices linked to other accounts.")
            for dev in shared_devs[:3]:
                lines.append(f"  - Device `{dev['device_id']}` shared with {dev['shared_with_count']} accounts ({', '.join(dev['connected_customers'][:4])})")
        else:
            lines.append("- **Shared Hardware Devices**: None detected.")

        if shared_pms:
            lines.append(f"- **Shared Payment Instruments**: {len(shared_pms)} cards/VPAs linked to other accounts.")
            for pm in shared_pms[:3]:
                lines.append(f"  - Payment `{pm['payment_method_id']}` shared with {pm['shared_with_count']} accounts ({', '.join(pm['connected_customers'][:4])})")
        else:
            lines.append("- **Shared Payment Instruments**: None detected.")

        # Protective Factors
        protective = evidence_data.get("protective_factors", [])
        if protective:
            lines.extend([
                "",
                "## 3. Mitigating & Protective Factors",
            ])
            for p in protective:
                lines.append(f"- **{p.get('signal')}**: {p.get('description')}")

        lines.extend([
            "",
            "## 4. Recommended Investigator Action Plan",
        ])

        recommendations = evidence_data.get("recommendations", [])
        if not recommendations:
            # Generate default based on evidence
            if shared_pms:
                recommendations.append("Review transaction volume routed through shared payment instruments.")
            if shared_devs:
                recommendations.append("Examine account creation fingerprints for hardware devices sharing this endpoint.")
            if ring_id and ring_id != "None (Isolated Node)":
                recommendations.append(f"Investigate cross-account co-transactions within syndicate {ring_id}.")
            if not recommendations:
                recommendations.append("Standard periodic monitoring. No immediate escalation needed.")

        for idx, rec in enumerate(recommendations, 1):
            lines.append(f"{idx}. {rec}")

        lines.append("============================================================")
        return "\n".join(lines)

    @staticmethod
    def generate_ring_report(ring_data: Dict[str, Any]) -> str:
        """Generates markdown investigation dossier for a fraud ring."""
        ring_id = ring_data.get("entity_id", "Unknown")
        risk_score = ring_data.get("risk_score", 0.0)
        risk_level = ring_data.get("risk_level", "HIGH")
        conf = ring_data.get("explanation_confidence", "HIGH")
        cust_count = ring_data.get("customer_count", 0)
        txn_count = ring_data.get("transaction_count", 0)
        volume = ring_data.get("transaction_volume", 0.0)
        dev_count = ring_data.get("shared_devices_count", 0)
        pm_count = ring_data.get("shared_payments_count", 0)

        lines = [
            "# FRAUDGRAPH SYNDICATE INVESTIGATION DOSSIER",
            "============================================================",
            f"**Syndicate Identifier**: Fraud Ring `{ring_id}`",
            f"**Network Risk Rating**: `{risk_score:.1f} / 100` ({risk_level})",
            f"**Investigation Confidence**: `{conf}`",
            f"**Syndicate Scale**: {cust_count} Member Accounts | {txn_count} Transactions",
            f"**Total Rupee Volume**: ₹{volume:,.2f}",
            "------------------------------------------------------------",
            "",
            "## 1. Syndicate Shared Infrastructure",
            f"- **Shared Hardware Devices**: {dev_count}",
            f"- **Shared Payment Instruments**: {pm_count}",
            "",
            "## 2. Key Forensic Findings",
        ]

        for idx, ev in enumerate(ring_data.get("evidence", []), 1):
            lines.append(f"{idx}. [{ev.get('severity', 'HIGH')}] {ev.get('description')}")

        lines.extend([
            "",
            "## 3. High-Priority Member Accounts",
        ])

        members = ring_data.get("top_members", [])
        if members:
            for m in members[:8]:
                m_id = m.get("customer_id", "Unknown")
                m_score = m.get("composite_risk_score", m.get("network_risk_score", 0.0))
                m_role = m.get("member_role", "MEMBER")
                lines.append(f"- Account `{m_id}` | Role: `{m_role}` | Risk Score: `{m_score:.1f}`")
        else:
            lines.append("- No member records listed.")

        lines.extend([
            "",
            "## 4. Recommended Syndicate Disruption Steps",
            "1. Cross-reference shared payment credentials against issuer chargeback alerts.",
            "2. Block transaction authorization on compromised shared hardware device fingerprints.",
            "3. Audit merchant settlement accounts receiving concentrated syndicate transfers.",
            "============================================================",
        ])
        return "\n".join(lines)
