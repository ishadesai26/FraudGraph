"""Data Repository and Forensic Subgraph Service for FraudGraph Phase 5 API."""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import networkx as nx

from backend.config.settings import get_settings
from backend.graph.graph_builder import GraphBuilder
from backend.explainability.investigation_engine import InvestigationEngine
from backend.api.schemas import (
    DashboardStatsResponse,
    RiskDistribution,
    KeyEntitySummary,
    CustomerSummary,
    CustomerDetailResponse,
    TransactionDetailResponse,
    FraudRingSummary,
    FraudRingDetailResponse,
    RingMemberSummary,
    EvidenceItem,
    ContributingSignal,
    ProtectiveFactor,
    SharedResource,
    ConnectedNeighbor,
    TimelineEvent,
    NetworkGraphResponse,
    NetworkNode,
    NetworkNodeData,
    NetworkEdge,
    NetworkEdgeData,
)


class DataService:
    """Singleton service providing cached data access and subgraphs for the FastAPI backend."""

    _instance: Optional["DataService"] = None

    def __init__(self):
        settings = get_settings()
        self.raw_dir = settings.raw_data_dir
        self.processed_dir = settings.processed_data_dir
        self.reports_dir = self.processed_dir / "investigation_reports"

        # Raw datasets
        self.builder = GraphBuilder(data_dir=self.raw_dir)
        self.datasets: Dict[str, pd.DataFrame] = self.builder.load_datasets()

        # Graphs
        self.H = self.builder.build_heterogeneous_graph(self.datasets)
        self.G_cust = self.builder.build_customer_projection_graph(self.datasets)

        # Processed tables
        rings_path = self.processed_dir / "fraud_rings.csv"
        self.rings_df = pd.read_csv(rings_path) if rings_path.exists() else pd.DataFrame()

        members_path = self.processed_dir / "ring_members.csv"
        self.members_df = pd.read_csv(members_path) if members_path.exists() else pd.DataFrame()

        # Investigation Engine
        self.investigation_engine = InvestigationEngine(
            datasets=self.datasets,
            H=self.H,
            G_cust=self.G_cust,
            rings_df=self.rings_df,
            members_df=self.members_df,
        )

        # Searchable Index & Summary
        index_path = self.processed_dir / "investigation_index.json"
        if index_path.exists():
            with open(index_path, "r", encoding="utf-8") as f:
                self.index_data = json.load(f)
        else:
            self.index_data = []

        summary_path = self.processed_dir / "investigation_summary.json"
        if summary_path.exists():
            with open(summary_path, "r", encoding="utf-8") as f:
                self.summary_data = json.load(f)
        else:
            self.summary_data = {}

        # Pre-index customers map for O(1) searches
        self.customer_meta = {
            row["customer_id"]: row for _, row in self.datasets["customers"].iterrows()
        }
        self.customer_txns = self.datasets["transactions"].groupby("customer_id")
        self.transactions_meta = {
            str(row["transaction_id"]): row for _, row in self.datasets["transactions"].iterrows()
        }

        # Ensure all 2,000 customers exist in index_data
        existing_cust_ids = {
            item["entity_id"] for item in self.index_data if item.get("entity_type") == "customer"
        }
        for c_id in self.customer_meta.keys():
            if c_id not in existing_cust_ids:
                self.index_data.append({
                    "entity_id": c_id,
                    "entity_type": "customer",
                    "risk_score": 5.0,
                    "risk_level": "LOW",
                    "ring_id": None,
                    "top_signal": "normal_activity",
                    "community_size": 0,
                })

    @classmethod
    def get_instance(cls) -> "DataService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_dashboard_stats(self) -> DashboardStatsResponse:
        """Calculates real high-level dashboard metrics and risk distributions."""
        cust_df = self.datasets["customers"]
        txns_df = self.datasets["transactions"]

        # Calculate risk distribution across all indexed entities
        risk_dist = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
        for item in self.index_data:
            if item.get("entity_type") == "customer":
                lvl = item.get("risk_level", "LOW")
                if lvl in risk_dist:
                    risk_dist[lvl] += 1

        high_cnt = risk_dist["HIGH"]
        crit_cnt = risk_dist["CRITICAL"]

        # Suspicious volume across rings
        suspicious_vol = float(self.rings_df["transaction_volume"].sum()) if not self.rings_df.empty and "transaction_volume" in self.rings_df.columns else 0.0

        highest_cust_info = self.summary_data.get("highest_risk_customer", {})
        highest_ring_info = self.summary_data.get("highest_risk_ring", {})

        return DashboardStatsResponse(
            total_customers=len(cust_df),
            total_transactions=len(txns_df),
            total_fraud_rings=len(self.rings_df),
            high_risk_customers_count=high_cnt,
            critical_customers_count=crit_cnt,
            suspicious_transaction_volume=suspicious_vol,
            risk_distribution=RiskDistribution(**risk_dist),
            top_detected_signals=self.summary_data.get("top_detected_signals", [
                "shared_device_cluster",
                "shared_payment_instrument",
                "proxy_ip_routing",
                "temporal_burst_synchronization",
            ]),
            highest_risk_customer=KeyEntitySummary(
                entity_id=highest_cust_info.get("customer_id"),
                risk_score=highest_cust_info.get("risk_score"),
                risk_level=highest_cust_info.get("risk_level"),
                detail=f"Associated with {highest_cust_info.get('associated_ring_id', 'Syndicate')}",
            ),
            highest_risk_ring=KeyEntitySummary(
                entity_id=highest_ring_info.get("ring_id"),
                risk_score=highest_ring_info.get("risk_score"),
                risk_level=highest_ring_info.get("risk_level"),
                detail=f"{highest_ring_info.get('customer_count', 0)} members · ₹{highest_ring_info.get('transaction_volume', 0.0):,.2f}",
            ),
        )

    def get_customers(
        self,
        page: int = 1,
        page_size: int = 25,
        risk_level: Optional[str] = None,
        ring_id: Optional[str] = None,
        min_risk_score: Optional[float] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[CustomerSummary], int, int]:
        """Filters, searches, and paginates customer records."""
        # Filter from index
        filtered = [x for x in self.index_data if x.get("entity_type") == "customer"]

        if risk_level:
            filtered = [x for x in filtered if str(x.get("risk_level", "")).upper() == risk_level.upper()]

        if ring_id:
            filtered = [x for x in filtered if str(x.get("ring_id", "")).upper() == ring_id.upper()]

        if min_risk_score is not None:
            filtered = [x for x in filtered if float(x.get("risk_score", 0.0)) >= min_risk_score]

        if search:
            s = search.strip().lower()
            filtered = [
                x for x in filtered
                if s in str(x.get("entity_id", "")).lower()
                or s in str(x.get("ring_id", "")).lower()
                or s in str(x.get("top_signal", "")).lower()
            ]

        # Sort by risk score descending
        filtered.sort(key=lambda x: float(x.get("risk_score", 0.0)), reverse=True)

        total = len(filtered)
        page_size = max(1, min(page_size, 100))
        total_pages = (total + page_size - 1) // page_size if total > 0 else 1
        page = max(1, min(page, total_pages))

        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_items = filtered[start_idx:end_idx]

        summaries = []
        for item in page_items:
            c_id = item["entity_id"]
            meta = self.customer_meta.get(c_id, {})
            # Spend calculation
            txns = self.datasets["transactions"][self.datasets["transactions"]["customer_id"] == c_id]
            summaries.append(CustomerSummary(
                customer_id=c_id,
                name=str(meta.get("name", f"Customer {c_id}")),
                risk_score=float(item.get("risk_score", 0.0)),
                risk_level=str(item.get("risk_level", "LOW")),
                ring_id=item.get("ring_id"),
                top_signal=str(item.get("top_signal", "normal_activity")),
                total_transactions=len(txns),
                total_spend=round(float(txns["amount"].sum()), 2) if not txns.empty else 0.0,
                home_city=str(meta.get("city", "Unknown")) if not pd.isna(meta.get("city")) else "Unknown",
            ))

        return summaries, total, total_pages

    def get_customer_detail(self, customer_id: str) -> Optional[CustomerDetailResponse]:
        """Retrieves full investigation dossier for a customer."""
        if customer_id not in self.customer_meta:
            # Check if digits were supplied (e.g. 28 -> CUST_00028)
            if customer_id.isdigit():
                customer_id = f"CUST_{int(customer_id):05d}"
            if customer_id not in self.customer_meta:
                return None

        # Check existing JSON report artifact
        rep_file = self.reports_dir / f"{customer_id}.json"
        if rep_file.exists():
            with open(rep_file, "r", encoding="utf-8") as f:
                exp = json.load(f)
        else:
            exp = self.investigation_engine.explain_entity(customer_id)

        if "error" in exp:
            return None

        meta = self.customer_meta.get(customer_id, {})
        net_details = exp.get("network_details", {})

        # Format shared resources
        shared_devs = [
            SharedResource(
                resource_id=d.get("device_id", "Unknown"),
                resource_type="DEVICE",
                shared_with_count=d.get("shared_with_count", 0),
                connected_customers=d.get("connected_customers", []),
            )
            for d in net_details.get("shared_devices", [])
        ]

        shared_pms = [
            SharedResource(
                resource_id=p.get("payment_method_id", "Unknown"),
                resource_type="PAYMENT_METHOD",
                shared_with_count=p.get("shared_with_count", 0),
                connected_customers=p.get("connected_customers", []),
            )
            for p in net_details.get("shared_payments", [])
        ]

        # Timeline
        timeline = [
            TimelineEvent(
                transaction_id=t.get("transaction_id"),
                timestamp=t.get("timestamp"),
                amount=float(t.get("amount", 0.0)),
                merchant_id=t.get("merchant_id", "Unknown"),
                payment_type=t.get("payment_type", "Unknown"),
                device_id=t.get("device_id", "Unknown"),
                ip_id=t.get("ip_id", "Unknown"),
                city=t.get("city", "Unknown"),
                seconds_since_previous=t.get("seconds_since_previous"),
                is_burst=bool(t.get("is_burst", False)),
                tags=t.get("tags", []),
            )
            for t in exp.get("timeline", [])
        ]

        return CustomerDetailResponse(
            customer_id=customer_id,
            name=str(meta.get("name", f"Customer {customer_id}")),
            home_city=str(meta.get("city", "Unknown")) if not pd.isna(meta.get("city")) else "Unknown",
            account_age_days=int(meta.get("account_age_days", 0)) if not pd.isna(meta.get("account_age_days")) else None,
            kyc_verified=bool(meta.get("kyc_verified", True)) if not pd.isna(meta.get("kyc_verified")) else None,
            risk_score=float(exp.get("risk_score", 0.0)),
            risk_level=str(exp.get("risk_level", "LOW")),
            explanation_confidence=str(exp.get("explanation_confidence", "LOW")),
            associated_ring_id=exp.get("associated_ring_id"),
            member_role=exp.get("member_role"),
            total_transactions=int(exp.get("total_transactions", len(timeline))),
            total_spend=float(exp.get("total_spend", sum(t.amount for t in timeline))),
            evidence=[
                EvidenceItem(
                    source=e.get("source"),
                    signal=e.get("signal", "risk_factor"),
                    severity=e.get("severity", "MEDIUM"),
                    description=e.get("description", ""),
                    value=e.get("value"),
                    importance=e.get("importance"),
                )
                for e in exp.get("evidence", [])
            ],
            protective_factors=[
                ProtectiveFactor(
                    signal=p.get("signal", ""),
                    description=p.get("description", ""),
                )
                for p in exp.get("protective_factors", [])
            ],
            contributing_signals=[
                ContributingSignal(
                    name=s.get("name", ""),
                    value=float(s.get("value", 0.0)),
                    importance=float(s.get("importance", 0.0)),
                )
                for s in exp.get("contributing_signals", [])
            ],
            shared_devices=shared_devs,
            shared_payments=shared_pms,
            connected_neighbors=[
                ConnectedNeighbor(
                    customer_id=str(n.get("customer_id", "")) if isinstance(n, dict) else str(n),
                    relational_weight=float(n.get("relational_weight", 1.0)) if isinstance(n, dict) else 1.0,
                )
                for n in net_details.get("connected_neighbors", [])
            ],
            recommendations=exp.get("recommendations", []),
            timeline=timeline,
            investigation_report_markdown=exp.get("investigation_report_markdown"),
        )

    def get_transaction_detail(self, transaction_id: str) -> Optional[TransactionDetailResponse]:
        """Retrieves forensic transaction detail and customer linkage."""
        if transaction_id not in self.transactions_meta:
            return None

        row = self.transactions_meta[transaction_id]
        cust_id = str(row["customer_id"])

        # Fetch customer explanation for context
        cust_detail = self.get_customer_detail(cust_id)
        if not cust_detail:
            return None

        return TransactionDetailResponse(
            transaction_id=transaction_id,
            customer_id=cust_id,
            merchant_id=str(row["merchant_id"]),
            amount=float(row["amount"]),
            timestamp=str(row["timestamp"]),
            payment_type=str(row.get("payment_type", "Unknown")),
            device_id=str(row.get("device_id", "Unknown")),
            ip_id=str(row.get("ip_id", "Unknown")),
            city=str(row.get("city", "Unknown")),
            is_flagged_fraud=bool(row.get("is_fraud", False)) if "is_fraud" in row else None,
            risk_score=cust_detail.risk_score,
            risk_level=cust_detail.risk_level,
            explanation_confidence=cust_detail.explanation_confidence,
            associated_ring_id=cust_detail.associated_ring_id,
            evidence=cust_detail.evidence,
            protective_factors=cust_detail.protective_factors,
            contributing_signals=cust_detail.contributing_signals,
            recommendations=cust_detail.recommendations,
            timeline=cust_detail.timeline,
        )

    def get_fraud_rings(
        self,
        page: int = 1,
        page_size: int = 25,
    ) -> Tuple[List[FraudRingSummary], int, int]:
        """Retrieves paginated detected fraud ring syndicates."""
        if self.rings_df.empty:
            return [], 0, 1

        total = len(self.rings_df)
        page_size = max(1, min(page_size, 100))
        total_pages = (total + page_size - 1) // page_size if total > 0 else 1
        page = max(1, min(page, total_pages))

        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_df = self.rings_df.iloc[start_idx:end_idx]

        summaries = []
        for _, row in page_df.iterrows():
            r_score = float(row.get("risk_score", row.get("network_risk_score", 0.0)))
            r_lvl = "CRITICAL" if r_score >= 80 else ("HIGH" if r_score >= 60 else "MEDIUM")
            
            # Parse top signals from string
            sig_str = str(row.get("risk_signals", ""))
            top_sigs = [s.strip() for s in sig_str.split(";") if s.strip()]

            summaries.append(FraudRingSummary(
                ring_id=str(row["ring_id"]),
                risk_score=r_score,
                risk_level=r_lvl,
                customer_count=int(row.get("customer_count", 0)),
                transaction_count=int(row.get("transaction_count", 0)),
                transaction_volume=float(row.get("transaction_volume", 0.0)),
                shared_devices_count=int(row.get("shared_device_count", 0)),
                shared_payments_count=int(row.get("shared_payment_count", 0)),
                shared_ips_count=int(row.get("shared_ip_count", 0)),
                top_signals=top_sigs[:4],
            ))

        return summaries, total, total_pages

    def get_fraud_ring_detail(self, ring_id: str) -> Optional[FraudRingDetailResponse]:
        """Retrieves complete forensic dossier for a specific fraud ring."""
        rep_file = self.reports_dir / f"{ring_id}.json"
        if rep_file.exists():
            with open(rep_file, "r", encoding="utf-8") as f:
                exp = json.load(f)
        else:
            exp = self.investigation_engine.explain_entity(ring_id)

        if "error" in exp:
            return None

        # Fetch members from members_df
        m_list = []
        if not self.members_df.empty:
            m_rows = self.members_df[self.members_df["ring_id"] == ring_id]
            for _, m in m_rows.iterrows():
                m_list.append(RingMemberSummary(
                    customer_id=str(m["customer_id"]),
                    individual_risk_score=float(m.get("individual_risk_score", 0.0)),
                    network_risk_score=float(m.get("network_risk_score", 0.0)),
                    is_core_member=bool(m.get("is_core_member", False)),
                ))

        return FraudRingDetailResponse(
            ring_id=ring_id,
            risk_score=float(exp.get("risk_score", 0.0)),
            risk_level=str(exp.get("risk_level", "HIGH")),
            explanation_confidence=str(exp.get("explanation_confidence", "HIGH")),
            customer_count=int(exp.get("customer_count", len(m_list))),
            transaction_count=int(exp.get("transaction_count", 0)),
            transaction_volume=float(exp.get("transaction_volume", 0.0)),
            shared_devices_count=int(exp.get("shared_devices_count", 0)),
            shared_payments_count=int(exp.get("shared_payments_count", 0)),
            shared_ips_count=int(exp.get("shared_ips_count", 0)),
            merchant_targets_count=int(exp.get("merchant_targets_count", 0)),
            evidence=[
                EvidenceItem(
                    source="GRAPH_NETWORK",
                    signal=e.get("signal", "syndicate_link"),
                    severity=e.get("severity", "HIGH"),
                    description=e.get("description", ""),
                    value=e.get("value"),
                    importance=e.get("importance"),
                )
                for e in exp.get("evidence", [])
            ],
            members=m_list,
            recommendations=exp.get("recommendations", []),
            investigation_report_markdown=exp.get("investigation_report_markdown"),
        )

    def get_investigation_report(self, entity_type: str, entity_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves raw Phase 4 investigation JSON."""
        clean_type = entity_type.lower()
        if clean_type in ["customer", "cust"]:
            prefix = "CUST_"
        elif clean_type in ["ring", "fraud_ring", "fraud-ring", "fr"]:
            prefix = "FR_"
        elif clean_type in ["transaction", "txn"]:
            prefix = "TXN_"
        else:
            return None

        # Check existing JSON
        target_id = entity_id
        if not target_id.startswith(prefix) and target_id.isdigit():
            if prefix == "CUST_":
                target_id = f"CUST_{int(target_id):05d}"
            elif prefix == "FR_":
                target_id = f"FR_{int(target_id):03d}"
            elif prefix == "TXN_":
                target_id = f"TXN_{int(target_id):05d}"

        rep_file = self.reports_dir / f"{target_id}.json"
        if rep_file.exists():
            with open(rep_file, "r", encoding="utf-8") as f:
                return json.load(f)

        res = self.investigation_engine.explain_entity(target_id)
        return res if "error" not in res else None

    def get_network_subgraph(
        self,
        entity_type: str,
        entity_id: str,
        max_hops: int = 2,
        max_nodes: int = 75,
    ) -> Optional[NetworkGraphResponse]:
        """Extracts localized, clean Cytoscape-formatted subgraphs."""
        clean_type = entity_type.lower()

        if clean_type in ["customer", "cust"]:
            target_id = entity_id if entity_id.startswith("CUST_") else f"CUST_{int(entity_id):05d}"
            if target_id not in self.H:
                return None
            return self._build_customer_subgraph(target_id, max_nodes=max_nodes)

        elif clean_type in ["ring", "fraud_ring", "fraud-ring", "fr"]:
            target_id = entity_id if entity_id.startswith("FR_") else f"FR_{int(entity_id):03d}"
            return self._build_ring_subgraph(target_id, max_nodes=max_nodes)

        elif clean_type in ["transaction", "txn"]:
            target_id = entity_id if entity_id.startswith("TXN_") else f"TXN_{int(entity_id):05d}"
            if target_id not in self.H:
                return None
            return self._build_transaction_subgraph(target_id)

        return None

    def _build_customer_subgraph(self, customer_id: str, max_nodes: int = 75) -> NetworkGraphResponse:
        """Constructs 1-2 hop neighborhood graph around a customer."""
        nodes_dict: Dict[str, NetworkNode] = {}
        edges_dict: Dict[str, NetworkEdge] = {}

        # Center customer node
        c_detail = self.get_customer_detail(customer_id)
        score = c_detail.risk_score if c_detail else 50.0
        lvl = c_detail.risk_level if c_detail else "MEDIUM"

        nodes_dict[customer_id] = NetworkNode(
            data=NetworkNodeData(
                id=customer_id,
                label=customer_id,
                type="customer",
                risk_score=score,
                risk_level=lvl,
                subtext="Primary Focus",
            )
        )

        # 1-hop outgoing / incoming neighbors in H
        for nbr in self.H.neighbors(customer_id):
            if len(nodes_dict) >= max_nodes:
                break
            nbr_type = self.H.nodes[nbr].get("type", "entity")
            nodes_dict[nbr] = NetworkNode(
                data=NetworkNodeData(
                    id=nbr,
                    label=nbr,
                    type=nbr_type,
                    subtext=nbr_type.replace("_", " ").title(),
                )
            )
            # Edge
            edge_id = f"e_{customer_id}_{nbr}"
            edge_data = self.H.get_edge_data(customer_id, nbr, 0) or {}
            edges_dict[edge_id] = NetworkEdge(
                data=NetworkEdgeData(
                    id=edge_id,
                    source=customer_id,
                    target=nbr,
                    type=str(edge_data.get("relation", "CONNECTED")),
                    label=str(edge_data.get("relation", "CONNECTED")),
                )
            )

        # Connected Customers via G_cust (Shared devices / cards)
        if customer_id in self.G_cust:
            for c_nbr in self.G_cust.neighbors(customer_id):
                if len(nodes_dict) >= max_nodes:
                    break
                if c_nbr not in nodes_dict:
                    nbr_detail = self.get_customer_detail(c_nbr)
                    n_score = nbr_detail.risk_score if nbr_detail else 50.0
                    n_lvl = nbr_detail.risk_level if nbr_detail else "MEDIUM"
                    nodes_dict[c_nbr] = NetworkNode(
                        data=NetworkNodeData(
                            id=c_nbr,
                            label=c_nbr,
                            type="customer",
                            risk_score=n_score,
                            risk_level=n_lvl,
                            subtext=f"Linked ({n_lvl})",
                        )
                    )

                edge_id = f"e_cust_{customer_id}_{c_nbr}"
                if edge_id not in edges_dict and f"e_cust_{c_nbr}_{customer_id}" not in edges_dict:
                    w = float(self.G_cust[customer_id][c_nbr].get("weight", 1.0))
                    edges_dict[edge_id] = NetworkEdge(
                        data=NetworkEdgeData(
                            id=edge_id,
                            source=customer_id,
                            target=c_nbr,
                            type="CO_CONNECTED",
                            label="SHARED_RESOURCE",
                            weight=w,
                        )
                    )

        # Associated ring node
        if c_detail and c_detail.associated_ring_id and c_detail.associated_ring_id != "None (Isolated Node)":
            r_id = c_detail.associated_ring_id
            nodes_dict[r_id] = NetworkNode(
                data=NetworkNodeData(
                    id=r_id,
                    label=r_id,
                    type="ring",
                    risk_score=100.0,
                    risk_level="CRITICAL",
                    subtext="Syndicate",
                )
            )
            r_edge = f"e_{customer_id}_{r_id}"
            edges_dict[r_edge] = NetworkEdge(
                data=NetworkEdgeData(
                    id=r_edge,
                    source=customer_id,
                    target=r_id,
                    type="MEMBER_OF",
                    label="MEMBER_OF",
                )
            )

        return NetworkGraphResponse(
            nodes=list(nodes_dict.values()),
            edges=list(edges_dict.values()),
            center_node_id=customer_id,
            total_nodes=len(nodes_dict),
            total_edges=len(edges_dict),
        )

    def _build_ring_subgraph(self, ring_id: str, max_nodes: int = 75) -> NetworkGraphResponse:
        """Constructs syndicate graph showing members, shared devices, and payment instruments."""
        nodes_dict: Dict[str, NetworkNode] = {}
        edges_dict: Dict[str, NetworkEdge] = {}

        # Ring center node
        ring_detail = self.get_fraud_ring_detail(ring_id)
        r_score = ring_detail.risk_score if ring_detail else 90.0
        r_lvl = ring_detail.risk_level if ring_detail else "HIGH"

        nodes_dict[ring_id] = NetworkNode(
            data=NetworkNodeData(
                id=ring_id,
                label=ring_id,
                type="ring",
                risk_score=r_score,
                risk_level=r_lvl,
                subtext="Syndicate Core",
            )
        )

        # Ring member customers
        if not self.members_df.empty:
            m_rows = self.members_df[self.members_df["ring_id"] == ring_id]
            for _, m in m_rows.head(20).iterrows():
                c_id = str(m["customer_id"])
                c_score = float(m.get("individual_risk_score", 50.0))
                c_lvl = "CRITICAL" if c_score >= 80 else ("HIGH" if c_score >= 60 else "MEDIUM")
                nodes_dict[c_id] = NetworkNode(
                    data=NetworkNodeData(
                        id=c_id,
                        label=c_id,
                        type="customer",
                        risk_score=c_score,
                        risk_level=c_lvl,
                        subtext="Core Member" if m.get("is_core_member") else "Member",
                    )
                )
                e_id = f"e_{c_id}_{ring_id}"
                edges_dict[e_id] = NetworkEdge(
                    data=NetworkEdgeData(
                        id=e_id,
                        source=c_id,
                        target=ring_id,
                        type="MEMBER_OF",
                        label="MEMBER_OF",
                    )
                )

                # Connect member shared devices / payment methods
                if c_id in self.H:
                    for nbr in self.H.neighbors(c_id):
                        if len(nodes_dict) >= max_nodes:
                            break
                        nbr_type = self.H.nodes[nbr].get("type", "entity")
                        if nbr_type in ["device", "payment_method", "ip"]:
                            nodes_dict[nbr] = NetworkNode(
                                data=NetworkNodeData(
                                    id=nbr,
                                    label=nbr,
                                    type=nbr_type,
                                    subtext=nbr_type.replace("_", " ").title(),
                                )
                            )
                            edge_id = f"e_{c_id}_{nbr}"
                            edges_dict[edge_id] = NetworkEdge(
                                data=NetworkEdgeData(
                                    id=edge_id,
                                    source=c_id,
                                    target=nbr,
                                    type="SHARED_INFRA",
                                    label="USES",
                                )
                            )

        return NetworkGraphResponse(
            nodes=list(nodes_dict.values()),
            edges=list(edges_dict.values()),
            center_node_id=ring_id,
            total_nodes=len(nodes_dict),
            total_edges=len(edges_dict),
        )

    def _build_transaction_subgraph(self, transaction_id: str) -> NetworkGraphResponse:
        """Constructs transaction localized graph."""
        nodes_dict: Dict[str, NetworkNode] = {}
        edges_dict: Dict[str, NetworkEdge] = {}

        t_row = self.transactions_meta.get(transaction_id)
        if not t_row:
            return NetworkGraphResponse(nodes=[], edges=[], total_nodes=0, total_edges=0)

        cust_id = str(t_row["customer_id"])
        merch_id = str(t_row.get("merchant_id", "Unknown"))
        dev_id = str(t_row.get("device_id", "Unknown"))
        ip_id = str(t_row.get("ip_id", "Unknown"))
        pm_id = str(t_row.get("payment_method_id", "Unknown"))

        # Transaction Node
        nodes_dict[transaction_id] = NetworkNode(
            data=NetworkNodeData(
                id=transaction_id,
                label=transaction_id,
                type="transaction",
                subtext=f"₹{float(t_row['amount']):,.2f}",
            )
        )

        # Customer Node
        nodes_dict[cust_id] = NetworkNode(
            data=NetworkNodeData(
                id=cust_id,
                label=cust_id,
                type="customer",
                subtext="Initiator",
            )
        )
        edges_dict[f"e_{cust_id}_{transaction_id}"] = NetworkEdge(
            data=NetworkEdgeData(
                id=f"e_{cust_id}_{transaction_id}",
                source=cust_id,
                target=transaction_id,
                type="INITIATED",
                label="INITIATED",
            )
        )

        # Connected entities
        for ent_id, ent_type in [(merch_id, "merchant"), (dev_id, "device"), (ip_id, "ip"), (pm_id, "payment_method")]:
            if ent_id and ent_id != "Unknown":
                nodes_dict[ent_id] = NetworkNode(
                    data=NetworkNodeData(
                        id=ent_id,
                        label=ent_id,
                        type=ent_type,
                        subtext=ent_type.replace("_", " ").title(),
                    )
                )
                edges_dict[f"e_{transaction_id}_{ent_id}"] = NetworkEdge(
                    data=NetworkEdgeData(
                        id=f"e_{transaction_id}_{ent_id}",
                        source=transaction_id,
                        target=ent_id,
                        type="ROUTED_TO",
                        label="ROUTED_TO",
                    )
                )

        return NetworkGraphResponse(
            nodes=list(nodes_dict.values()),
            edges=list(edges_dict.values()),
            center_node_id=transaction_id,
            total_nodes=len(nodes_dict),
            total_edges=len(edges_dict),
        )
