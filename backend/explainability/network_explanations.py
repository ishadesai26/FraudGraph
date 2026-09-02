"""Network and graph topological explanation engine for FraudGraph.

Extracts verifiable, quantitative relational evidence from Phase 2 heterogeneous graphs,
customer projection graphs, Louvain communities, and detected fraud rings.
"""

from typing import Dict, List, Optional, Any, Set
import numpy as np
import pandas as pd
import networkx as nx


class NetworkExplainer:
    """Extracts graph topological evidence and multi-hop entity sharing details."""

    def __init__(
        self,
        H: Optional[nx.MultiDiGraph] = None,
        G_cust: Optional[nx.Graph] = None,
        datasets: Optional[Dict[str, pd.DataFrame]] = None,
        graph_features_df: Optional[pd.DataFrame] = None,
        rings_df: Optional[pd.DataFrame] = None,
        members_df: Optional[pd.DataFrame] = None,
    ):
        self.H = H
        self.G_cust = G_cust
        self.datasets = datasets or {}
        self.graph_features_df = graph_features_df if graph_features_df is not None else pd.DataFrame()
        self.rings_df = rings_df if rings_df is not None else pd.DataFrame()
        self.members_df = members_df if members_df is not None else pd.DataFrame()

        self._gfeat_map = {}
        if not self.graph_features_df.empty and "customer_id" in self.graph_features_df.columns:
            self._gfeat_map = self.graph_features_df.set_index("customer_id").to_dict(orient="index")

    def explain_customer_network(self, customer_id: str) -> Dict[str, Any]:
        """Extracts complete network evidence and shared entity linkages for a customer."""
        evidence_items = []
        cust_feat = self._gfeat_map.get(customer_id, {})

        # 1. Ring and Community Membership
        ring_id = None
        net_risk = float(cust_feat.get("network_risk_score", 0.0))
        member_role = "MEMBER"

        if not self.members_df.empty:
            m_rows = self.members_df[self.members_df["customer_id"] == customer_id]
            if not m_rows.empty:
                ring_id = str(m_rows.iloc[0]["ring_id"])
                net_risk = float(m_rows.iloc[0].get("network_risk_score", net_risk))
                member_role = str(m_rows.iloc[0].get("member_role", "MEMBER"))

        # 2. Shared Hardware Devices
        shared_devices = []
        if self.H is not None and f"cust_{customer_id}" in self.H:
            # Query devices connected to customer
            out_edges = self.H.out_edges(f"cust_{customer_id}", data=True)
            for _, target, data in out_edges:
                if data.get("type") == "USES_DEVICE":
                    dev_id = target.replace("dev_", "")
                    # Find other customers using this device
                    in_edges = self.H.in_edges(target, data=True)
                    other_custs = [src.replace("cust_", "") for src, _, d in in_edges if d.get("type") == "USES_DEVICE" and src != f"cust_{customer_id}"]
                    if other_custs:
                        shared_devices.append({
                            "device_id": dev_id,
                            "shared_with_count": len(other_custs),
                            "connected_customers": other_custs[:5],
                        })

        if shared_devices:
            max_dev = max(shared_devices, key=lambda x: x["shared_with_count"])
            evidence_items.append({
                "signal": "shared_device_cluster",
                "severity": "CRITICAL" if max_dev["shared_with_count"] >= 4 else "HIGH",
                "count": len(shared_devices),
                "max_sharing_accounts": max_dev["shared_with_count"],
                "sample_device": max_dev["device_id"],
                "description": f"Customer shares hardware device {max_dev['device_id']} with {max_dev['shared_with_count']} other distinct accounts.",
            })

        # 3. Shared Payment Methods (Mule Cards / UPI)
        shared_payments = []
        if self.H is not None and f"cust_{customer_id}" in self.H:
            out_edges = self.H.out_edges(f"cust_{customer_id}", data=True)
            for _, target, data in out_edges:
                if data.get("type") == "USES_PAYMENT":
                    pm_id = target.replace("pm_", "")
                    in_edges = self.H.in_edges(target, data=True)
                    other_custs = [src.replace("cust_", "") for src, _, d in in_edges if d.get("type") == "USES_PAYMENT" and src != f"cust_{customer_id}"]
                    if other_custs:
                        shared_payments.append({
                            "payment_method_id": pm_id,
                            "shared_with_count": len(other_custs),
                            "connected_customers": other_custs[:5],
                        })

        if shared_payments:
            max_pm = max(shared_payments, key=lambda x: x["shared_with_count"])
            evidence_items.append({
                "signal": "shared_payment_instrument",
                "severity": "CRITICAL" if max_pm["shared_with_count"] >= 3 else "HIGH",
                "count": len(shared_payments),
                "max_sharing_accounts": max_pm["shared_with_count"],
                "sample_payment": max_pm["payment_method_id"],
                "description": f"Customer shares payment instrument {max_pm['payment_method_id']} with {max_pm['shared_with_count']} other accounts.",
            })

        # 4. Shared Datacenter / Proxy IPs
        shared_proxy_count = int(cust_feat.get("shared_proxy_count", 0))
        if shared_proxy_count > 0:
            evidence_items.append({
                "signal": "shared_proxy_infrastructure",
                "severity": "HIGH",
                "count": shared_proxy_count,
                "description": f"Customer shares {shared_proxy_count} Datacenter/VPN proxy IP addresses with other transacting accounts.",
            })

        # 5. Connected Neighbors in Customer Projection Graph
        connected_neighbors = []
        if self.G_cust is not None and customer_id in self.G_cust:
            neighbors = list(self.G_cust.neighbors(customer_id))
            for n in neighbors[:8]:
                w = self.G_cust[customer_id][n].get("weight", 1.0)
                connected_neighbors.append({
                    "customer_id": n,
                    "relational_weight": round(float(w), 2),
                })
            connected_neighbors.sort(key=lambda x: x["relational_weight"], reverse=True)

        # 6. Temporal Synchronization & Merchant Concentration
        sync_score = float(cust_feat.get("temporal_sync_score", 0.0))
        hhi = float(cust_feat.get("merchant_hhi", 0.0))

        if sync_score >= 0.25:
            evidence_items.append({
                "signal": "temporal_burst_synchronization",
                "severity": "HIGH" if sync_score >= 0.50 else "MEDIUM",
                "value": f"{sync_score*100:.1f}% synchronized",
                "description": f"{sync_score*100:.1f}% of customer transactions occurred within narrow synchronized bursts (< 180s).",
            })

        if hhi >= 0.40:
            evidence_items.append({
                "signal": "merchant_spend_concentration",
                "severity": "MEDIUM",
                "value": f"HHI: {hhi:.2f}",
                "description": f"Spend is heavily concentrated across few merchants (Herfindahl-Hirschman Index: {hhi:.2f}).",
            })

        return {
            "customer_id": customer_id,
            "ring_id": ring_id,
            "member_role": member_role,
            "network_risk_score": net_risk,
            "degree": int(cust_feat.get("degree", len(connected_neighbors))),
            "pagerank": float(cust_feat.get("pagerank", 0.0)),
            "betweenness_centrality": float(cust_feat.get("betweenness_centrality", 0.0)),
            "clustering_coefficient": float(cust_feat.get("clustering_coefficient", 0.0)),
            "shared_devices": shared_devices,
            "shared_payments": shared_payments,
            "connected_neighbors": connected_neighbors,
            "network_evidence": evidence_items,
        }

    def explain_fraud_ring(self, ring_id: str) -> Dict[str, Any]:
        """Extracts complete multi-entity profile and forensic dossier for a detected fraud ring."""
        if self.rings_df.empty or "ring_id" not in self.rings_df.columns:
            return {"ring_id": ring_id, "error": "No fraud rings loaded."}

        r_match = self.rings_df[self.rings_df["ring_id"] == ring_id]
        if r_match.empty:
            return {"ring_id": ring_id, "error": f"Fraud ring {ring_id} not found."}

        ring_row = r_match.iloc[0].to_dict()
        risk_score = float(ring_row.get("risk_score", ring_row.get("network_risk_score", 0.0)))
        
        # Get member list and member risk scores
        members = []
        if not self.members_df.empty:
            m_match = self.members_df[self.members_df["ring_id"] == ring_id]
            members = m_match.to_dict(orient="records")

        # Key evidence summary
        evidence = []
        if int(ring_row.get("shared_device_count", 0)) > 0:
            evidence.append({
                "signal": "syndicate_shared_devices",
                "severity": "HIGH",
                "count": int(ring_row["shared_device_count"]),
                "description": f"Syndicate shares {ring_row['shared_device_count']} hardware devices across {ring_row.get('customer_count', 0)} member accounts.",
            })
        if int(ring_row.get("shared_payment_count", 0)) > 0:
            evidence.append({
                "signal": "syndicate_shared_payment_methods",
                "severity": "CRITICAL",
                "count": int(ring_row["shared_payment_count"]),
                "description": f"Syndicate funnels transactions through {ring_row['shared_payment_count']} shared credit cards and UPI VPAs.",
            })
        sync_ratio = float(ring_row.get("time_synchronization_score", ring_row.get("temporal_sync_ratio", 0.0)))
        if sync_ratio > 0.001:
            sync_pct = sync_ratio * 100
            evidence.append({
                "signal": "coordinated_burst_timing",
                "severity": "HIGH",
                "value": f"{sync_pct:.2f}%",
                "description": f"{sync_pct:.2f}% of syndicate transactions occur in synchronized coordinated bursts.",
            })

        risk_tier = "CRITICAL" if risk_score >= 80.0 else ("HIGH" if risk_score >= 60.0 else ("MEDIUM" if risk_score >= 35.0 else "LOW"))

        return {
            "entity_id": ring_id,
            "risk_score": risk_score,
            "risk_level": risk_tier,
            "customer_count": int(ring_row.get("customer_count", len(members))),
            "transaction_count": int(ring_row.get("transaction_count", 0)),
            "transaction_volume": float(ring_row.get("transaction_volume", 0.0)),
            "shared_devices_count": int(ring_row.get("shared_device_count", 0)),
            "shared_ips_count": int(ring_row.get("shared_ip_count", 0)),
            "shared_payments_count": int(ring_row.get("shared_payment_count", 0)),
            "merchant_targets_count": int(ring_row.get("merchant_count", 0)),
            "evidence": evidence,
            "top_members": members[:15],  # Top members for summary
        }
