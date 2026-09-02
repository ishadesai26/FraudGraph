"""Structured Evidence Graph Builder for Phase 6 multi-agent explainability."""

from typing import Dict, Any, List
from backend.agents.schemas import EvidenceGraph, EvidenceGraphNode, EvidenceGraphEdge, AgentEvidenceItem


class EvidenceGraphBuilder:
    """Constructs a structured evidence graph linking entities, signals, and agent findings."""

    @staticmethod
    def build(
        entity_type: str,
        entity_id: str,
        evidence_items: List[AgentEvidenceItem],
        graph_data: Dict[str, Any],
        decision_status: str,
    ) -> EvidenceGraph:
        nodes: List[EvidenceGraphNode] = []
        edges: List[EvidenceGraphEdge] = []
        seen_nodes = set()

        def add_node(node_id: str, label: str, node_type: str, subtext: str = None, severity: str = None):
            if node_id not in seen_nodes:
                seen_nodes.add(node_id)
                nodes.append(
                    EvidenceGraphNode(
                        id=node_id,
                        label=label,
                        type=node_type,
                        subtext=subtext,
                        severity=severity,
                    )
                )

        def add_edge(source: str, target: str, edge_type: str, label: str = None):
            edge_id = f"e_{source}_{target}_{edge_type}"
            edges.append(
                EvidenceGraphEdge(
                    id=edge_id,
                    source=source,
                    target=target,
                    type=edge_type,
                    label=label or edge_type,
                )
            )

        # 1. Root Central Entity Node
        add_node(
            node_id=entity_id,
            label=entity_id,
            node_type=entity_type,
            subtext=f"Target {entity_type.title()}",
        )

        # 2. Decision Verdict Node
        decision_node_id = f"DECISION_{decision_status}"
        add_node(
            node_id=decision_node_id,
            label=decision_status.replace("_", " "),
            node_type="decision",
            subtext="Investigation Disposition",
        )
        add_edge(entity_id, decision_node_id, "RESULTS_IN")

        # 3. Evidence Signal Nodes & Edges
        for idx, ev in enumerate(evidence_items[:6]):
            signal_id = f"SIG_{idx}_{ev.signal}"
            add_node(
                node_id=signal_id,
                label=ev.signal.replace("_", " "),
                node_type="signal",
                subtext=f"Source: {ev.source_agent}",
                severity=ev.severity,
            )
            add_edge(entity_id, signal_id, "SUPPORTED_BY")
            add_edge(signal_id, decision_node_id, "CONTRIBUTES_TO")

        # 4. Infrastructure & Syndicate Nodes
        ring_id = graph_data.get("associated_ring_id") or graph_data.get("ring_id")
        if ring_id and str(ring_id).lower() not in ["none", "isolated", "none (isolated node)"]:
            add_node(
                node_id=ring_id,
                label=ring_id,
                node_type="fraud_ring",
                subtext="Syndicate Community",
            )
            add_edge(entity_id, ring_id, "PART_OF")

        for dev in graph_data.get("shared_devices", [])[:2]:
            dev_id = dev.get("resource_id", "DEV")
            add_node(
                node_id=dev_id,
                label=dev_id,
                node_type="device",
                subtext=f"Shared with {dev.get('shared_with_count', 0)} accounts",
            )
            add_edge(entity_id, dev_id, "CONNECTED_TO")

        for pm in graph_data.get("shared_payments", [])[:2]:
            pm_id = pm.get("resource_id", "PM")
            add_node(
                node_id=pm_id,
                label=pm_id,
                node_type="payment_method",
                subtext=f"Shared with {pm.get('shared_with_count', 0)} accounts",
            )
            add_edge(entity_id, pm_id, "CONNECTED_TO")

        return EvidenceGraph(nodes=nodes, edges=edges)
