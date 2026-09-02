"""Graph construction engine for FraudGraph fintech ecosystem.

Constructs:
1. Heterogeneous multi-partite graph H connecting:
   Customer, Transaction, Device, IP, PaymentMethod, Merchant, Location.
2. Homogeneous multi-relational Customer Projection Graph G_cust capturing:
   Shared devices, shared IPs, shared payment instruments, and co-transactions.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set, Any
from collections import defaultdict
from itertools import combinations
import pandas as pd
import networkx as nx

from backend.config.settings import get_settings


class GraphBuilder:
    """Builds heterogeneous payment graphs and homogeneous entity projections."""

    REQUIRED_FILES = [
        "customers.csv",
        "transactions.csv",
        "devices.csv",
        "ip_addresses.csv",
        "payment_methods.csv",
        "merchants.csv",
    ]

    def __init__(self, data_dir: Optional[Path] = None):
        settings = get_settings()
        self.data_dir = Path(data_dir) if data_dir is not None else settings.raw_data_dir
        self.datasets: Dict[str, pd.DataFrame] = {}
        self.hetero_graph: Optional[nx.MultiDiGraph] = None
        self.customer_graph: Optional[nx.Graph] = None

    def load_datasets(self) -> Dict[str, pd.DataFrame]:
        """Loads and caches Phase 1 CSV datasets."""
        for filename in self.REQUIRED_FILES:
            name = filename.replace(".csv", "")
            filepath = self.data_dir / filename
            if not filepath.exists():
                raise FileNotFoundError(f"Required dataset file not found: {filepath}")
            self.datasets[name] = pd.read_csv(filepath)
        return self.datasets

    def build_heterogeneous_graph(self, datasets: Optional[Dict[str, pd.DataFrame]] = None) -> nx.MultiDiGraph:
        """Constructs the complete heterogeneous multi-partite graph.
        
        Ground-truth labels (is_fraud, fraud_ring_id, fraud_type) are strictly excluded.
        """
        if datasets is None:
            if not self.datasets:
                self.load_datasets()
            datasets = self.datasets

        H = nx.MultiDiGraph()

        # 1. Customer Nodes
        cust_df = datasets["customers"]
        for _, row in cust_df.iterrows():
            H.add_node(
                row["customer_id"],
                node_type="Customer",
                label=row["customer_id"],
                age=int(row["customer_age"]),
                segment=str(row["customer_segment"]),
                account_age_days=int(row["account_age_days"]),
                country=str(row["country"]),
                city=str(row["city"]),
                account_created_at=str(row["account_created_at"]),
            )

        # 2. Device Nodes
        dev_df = datasets["devices"]
        for _, row in dev_df.iterrows():
            H.add_node(
                row["device_id"],
                node_type="Device",
                label=row["device_id"],
                device_type=str(row["device_type"]),
                os=str(row["os"]),
                device_age_days=int(row["device_age_days"]),
            )

        # 3. IP Nodes
        ip_df = datasets["ip_addresses"]
        for _, row in ip_df.iterrows():
            H.add_node(
                row["ip_id"],
                node_type="IP",
                label=row["ip_id"],
                ip_type=str(row["ip_type"]),
                country=str(row["country"]),
                city=str(row["city"]),
            )

        # 4. PaymentMethod Nodes
        pm_df = datasets["payment_methods"]
        for _, row in pm_df.iterrows():
            H.add_node(
                row["payment_method_id"],
                node_type="PaymentMethod",
                label=row["payment_method_id"],
                payment_type=str(row["payment_type"]),
                issuer_category=str(row["issuer_category"]),
            )

        # 5. Merchant Nodes
        merch_df = datasets["merchants"]
        for _, row in merch_df.iterrows():
            H.add_node(
                row["merchant_id"],
                node_type="Merchant",
                label=row["merchant_id"],
                category=str(row["merchant_category"]),
                size=str(row["merchant_size"]),
                city=str(row["city"]),
            )

        # 6. Location Nodes & Transaction Nodes + Edges
        txns_df = datasets["transactions"]
        locations_added: Set[str] = set()

        for _, row in txns_df.iterrows():
            t_id = row["transaction_id"]
            c_id = row["customer_id"]
            m_id = row["merchant_id"]
            d_id = row["device_id"]
            ip_id = row["ip_id"]
            pm_id = row["payment_method_id"]
            city = str(row["city"])
            loc_id = f"LOC_{city}"

            if loc_id not in locations_added:
                H.add_node(loc_id, node_type="Location", label=city, city=city)
                locations_added.add(loc_id)

            # Add Transaction Node (strictly excluding ground-truth fraud labels)
            H.add_node(
                t_id,
                node_type="Transaction",
                label=t_id,
                amount=float(row["amount"]),
                currency=str(row["currency"]),
                status=str(row["transaction_status"]),
                payment_type=str(row["payment_type"]),
                city=city,
                timestamp=str(row["timestamp"]),
            )

            # Heterogeneous directed edges connecting transaction event
            H.add_edge(c_id, t_id, edge_type="INITIATED", timestamp=str(row["timestamp"]))
            H.add_edge(t_id, m_id, edge_type="PAID_TO", amount=float(row["amount"]))
            H.add_edge(t_id, d_id, edge_type="TRANSACTED_ON")
            H.add_edge(t_id, ip_id, edge_type="ROUTED_THROUGH")
            H.add_edge(t_id, pm_id, edge_type="PAID_WITH")
            H.add_edge(t_id, loc_id, edge_type="LOCATED_IN")

            # Direct Customer -> Entity bipartite edges with accumulated weights
            H.add_edge(c_id, d_id, edge_type="USES_DEVICE", weight=1.0)
            H.add_edge(c_id, ip_id, edge_type="USES_IP", weight=1.0)
            H.add_edge(c_id, pm_id, edge_type="USES_PAYMENT", weight=1.0)

        self.hetero_graph = H
        return H

    def build_customer_projection_graph(self, datasets: Optional[Dict[str, pd.DataFrame]] = None) -> nx.Graph:
        """Constructs the homogeneous Customer-to-Customer relationship graph.
        
        Derives weighted relational linkages based on shared devices, shared IPs,
        shared payment methods, and synchronized co-merchant transactions.
        """
        if datasets is None:
            if not self.datasets:
                self.load_datasets()
            datasets = self.datasets

        cust_df = datasets["customers"]
        txns_df = datasets["transactions"]
        ip_df = datasets["ip_addresses"].set_index("ip_id")["ip_type"].to_dict()

        G_cust = nx.Graph()

        # Add all customer nodes
        for _, row in cust_df.iterrows():
            G_cust.add_node(
                row["customer_id"],
                node_type="Customer",
                label=row["customer_id"],
                age=int(row["customer_age"]),
                segment=str(row["customer_segment"]),
                account_age_days=int(row["account_age_days"]),
                city=str(row["city"]),
                account_created_at=str(row["account_created_at"]),
            )

        # Inverted index lookups: entity -> set of (customer_id, count)
        device_users: Dict[str, Set[str]] = defaultdict(set)
        ip_users: Dict[str, Set[str]] = defaultdict(set)
        pm_users: Dict[str, Set[str]] = defaultdict(set)

        # Also track temporal events: (merchant_id, timestamp_10min_window) -> set of customer_ids
        temporal_merchant_users: Dict[str, Set[str]] = defaultdict(set)

        for _, row in txns_df.iterrows():
            cid = row["customer_id"]
            did = row["device_id"]
            ipid = row["ip_id"]
            pmid = row["payment_method_id"]
            mid = row["merchant_id"]
            ts = pd.to_datetime(row["timestamp"])

            device_users[did].add(cid)
            ip_users[ipid].add(cid)
            pm_users[pmid].add(cid)

            # Round timestamp to 10-minute intervals for temporal co-transaction discovery
            time_bucket = ts.floor("10min")
            temporal_key = f"{mid}_{time_bucket.isoformat()}"
            temporal_merchant_users[temporal_key].add(cid)

        # Helper to safely update edge properties
        def _add_or_update_edge(u: str, v: str, edge_kind: str, entity_id: str, base_weight: float):
            if u == v:
                return
            if not G_cust.has_edge(u, v):
                G_cust.add_edge(
                    u,
                    v,
                    weight=0.0,
                    shared_devices=set(),
                    shared_ips=set(),
                    shared_pms=set(),
                    co_merchant_buckets=set(),
                    edge_types=set(),
                )
            edge_data = G_cust[u][v]
            edge_data["weight"] += base_weight
            edge_data["edge_types"].add(edge_kind)
            if edge_kind == "SHARED_DEVICE":
                edge_data["shared_devices"].add(entity_id)
            elif edge_kind == "SHARED_IP":
                edge_data["shared_ips"].add(entity_id)
            elif edge_kind == "SHARED_PAYMENT":
                edge_data["shared_pms"].add(entity_id)
            elif edge_kind == "CO_TRANSACTION":
                edge_data["co_merchant_buckets"].add(entity_id)

        # 1. Connect customers sharing devices (Strong indicator: weight = 3.5)
        for did, users in device_users.items():
            if len(users) > 1:
                for u, v in combinations(users, 2):
                    _add_or_update_edge(u, v, "SHARED_DEVICE", did, base_weight=3.5)

        # 2. Connect customers sharing payment methods (Very strong indicator: weight = 4.5)
        for pmid, users in pm_users.items():
            if len(users) > 1:
                for u, v in combinations(users, 2):
                    _add_or_update_edge(u, v, "SHARED_PAYMENT", pmid, base_weight=4.5)

        # 3. Connect customers sharing IPs (Moderate indicator: residential=1.0, datacenter/vpn=2.5)
        for ipid, users in ip_users.items():
            if len(users) > 1:
                iptype = ip_df.get(ipid, "RESIDENTIAL")
                ip_weight = 2.5 if iptype in ["DATACENTER", "VPN"] else 1.0
                for u, v in combinations(users, 2):
                    _add_or_update_edge(u, v, "SHARED_IP", ipid, base_weight=ip_weight)

        # 4. Connect customers with synchronized co-merchant transactions (weight = 2.0)
        for bucket, users in temporal_merchant_users.items():
            if len(users) > 1:
                for u, v in combinations(users, 2):
                    _add_or_update_edge(u, v, "CO_TRANSACTION", bucket, base_weight=2.0)

        # Convert set attributes to list/int summaries for clean serialization
        for u, v, data in G_cust.edges(data=True):
            data["num_shared_devices"] = len(data["shared_devices"])
            data["num_shared_ips"] = len(data["shared_ips"])
            data["num_shared_pms"] = len(data["shared_pms"])
            data["num_co_txns"] = len(data["co_merchant_buckets"])
            data["edge_type"] = "_".join(sorted(data["edge_types"]))

        self.customer_graph = G_cust
        return G_cust

    def export_graph_to_dataframes(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Exports graph nodes and edges into DataFrames suitable for CSV/Frontend export."""
        if self.hetero_graph is None:
            self.build_heterogeneous_graph()

        H = self.hetero_graph

        # Extract nodes rapidly
        node_records = []
        for n, d in H.nodes(data=True):
            ntype = d.get("node_type", "Unknown")
            label = d.get("label", str(n))
            meta_dict = {k: v for k, v in d.items() if k not in ["node_type", "label"]}
            node_records.append({
                "node_id": n,
                "node_type": ntype,
                "label": label,
                "metadata": json.dumps(meta_dict) if meta_dict else "{}",
            })
        nodes_df = pd.DataFrame(node_records)

        # Extract edges rapidly
        edge_records = []
        for u, v, k, d in H.edges(keys=True, data=True):
            etype = d.get("edge_type", "CONNECTED_TO")
            weight = float(d.get("weight", 1.0))
            meta_dict = {k: v for k, v in d.items() if k not in ["edge_type", "weight"]}
            edge_records.append({
                "source": u,
                "target": v,
                "edge_type": etype,
                "weight": weight,
                "metadata": json.dumps(meta_dict) if meta_dict else "{}",
            })
        edges_df = pd.DataFrame(edge_records)

        return nodes_df, edges_df
