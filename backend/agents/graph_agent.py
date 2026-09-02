"""Agent 2: Graph Agent — Evaluates heterogeneous graph topologies and syndicate rings."""

from typing import Dict, Any, List
from backend.agents.base_agent import BaseAgent
from backend.agents.schemas import AgentEvidenceItem


class GraphAgent(BaseAgent):
    """Specialized agent evaluating graph topology, shared infrastructure, and fraud syndicates."""

    def __init__(self):
        super().__init__(
            name="GraphAgent",
            description="Analyzes Phase 2 heterogeneous graph linkages, shared hardware/cards/IPs, and Louvain fraud rings.",
        )

    def _execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        evidence: List[AgentEvidenceItem] = []
        graph_data = context.get("graph_data", {})
        
        network_risk = float(graph_data.get("network_risk_score", 0.0))
        shared_devices = graph_data.get("shared_devices", [])
        shared_payments = graph_data.get("shared_payments", [])
        shared_ips = graph_data.get("shared_ips", [])
        ring_id = graph_data.get("associated_ring_id") or graph_data.get("ring_id")
        member_role = graph_data.get("member_role", "MEMBER")
        neighbors_count = len(graph_data.get("connected_neighbors", []))

        # 1. Syndicate Fraud Ring Association
        if ring_id and str(ring_id).lower() not in ["none", "isolated", "none (isolated node)"]:
            severity = "CRITICAL" if member_role == "CORE" or network_risk >= 80.0 else "HIGH"
            evidence.append(
                self.create_evidence(
                    signal="syndicate_ring_membership",
                    description=f"Identified as member of coordinated syndicate '{ring_id}' with role '{member_role}'.",
                    severity=severity,
                    value=ring_id,
                    importance=0.40,
                    category="GRAPH_TOPOLOGY",
                )
            )

        # 2. Shared Hardware Devices
        if shared_devices:
            max_dev_sharing = max([d.get("shared_with_count", 0) for d in shared_devices], default=len(shared_devices))
            evidence.append(
                self.create_evidence(
                    signal="shared_device_hardware_cluster",
                    description=f"Directly linked to {len(shared_devices)} hardware device(s) shared across up to {max_dev_sharing} accounts.",
                    severity="CRITICAL" if max_dev_sharing >= 4 else "HIGH",
                    value=len(shared_devices),
                    importance=0.35,
                    category="GRAPH_TOPOLOGY",
                )
            )

        # 3. Shared Payment Instruments (Cards/VPAs)
        if shared_payments:
            max_pm_sharing = max([p.get("shared_with_count", 0) for p in shared_payments], default=len(shared_payments))
            evidence.append(
                self.create_evidence(
                    signal="shared_payment_instrument_collusion",
                    description=f"Utilizes {len(shared_payments)} payment instrument(s) shared across {max_pm_sharing} separate customer accounts.",
                    severity="CRITICAL" if max_pm_sharing >= 3 else "HIGH",
                    value=len(shared_payments),
                    importance=0.35,
                    category="GRAPH_TOPOLOGY",
                )
            )

        # 4. Proxy / Shared IP Routing
        if shared_ips and len(shared_ips) >= 2:
            evidence.append(
                self.create_evidence(
                    signal="shared_network_ip_infrastructure",
                    description=f"Observed routing transactions across {len(shared_ips)} shared IP address endpoints.",
                    severity="MEDIUM",
                    value=len(shared_ips),
                    importance=0.20,
                    category="GRAPH_TOPOLOGY",
                )
            )

        # 5. Network Structural Centrality
        if network_risk >= 80.0:
            evidence.append(
                self.create_evidence(
                    signal="high_graph_structural_risk",
                    description=f"Graph centrality and multi-entity clustering score is exceptionally elevated ({network_risk:.1f}/100).",
                    severity="HIGH",
                    value=round(network_risk, 1),
                    importance=0.30,
                    category="GRAPH_TOPOLOGY",
                )
            )
        elif not shared_devices and not shared_payments and (not ring_id or str(ring_id).lower() in ["none", "isolated"]):
            evidence.append(
                self.create_evidence(
                    signal="isolated_graph_topology",
                    description="No shared hardware devices or payment instruments detected in graph topology.",
                    severity="LOW",
                    value=0,
                    importance=0.20,
                    category="PROTECTIVE",
                )
            )

        # Level determination
        net_level = "LOW"
        if network_risk >= 80.0 or (ring_id and member_role == "CORE"):
            net_level = "CRITICAL" if network_risk >= 90.0 else "HIGH"
        elif network_risk >= 50.0 or shared_devices or shared_payments:
            net_level = "MEDIUM"

        summary = (
            f"GraphAgent evaluated topology: Network Risk {network_risk:.1f} ({net_level}), "
            f"{len(shared_devices)} Shared Devices, {len(shared_payments)} Shared Cards, "
            f"Ring: {ring_id or 'None'}."
        )

        return {
            "network_risk_score": network_risk,
            "network_risk_level": net_level,
            "shared_devices_count": len(shared_devices),
            "shared_payments_count": len(shared_payments),
            "ring_id": ring_id,
            "evidence": evidence,
            "summary": summary,
        }
