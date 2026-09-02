"""Graph feature extraction module for FraudGraph fintech ecosystem.

Calculates topological, structural, and behavioral features for customer nodes:
- Degree and Weighted Degree
- Betweenness Centrality and PageRank
- Clustering Coefficients
- Resource Sharing Counts (Devices, IPs, Payment Instruments)
- Transaction Frequency, Volume, and Velocity
- Merchant Concentration (HHI)
- Temporal Synchronization and Burstiness
- Geographic Spread
"""

from typing import Dict, List, Optional, Any
from collections import Counter
import numpy as np
import pandas as pd
import networkx as nx


class GraphFeatureExtractor:
    """Calculates network and behavioral features across heterogeneous and projection graphs."""

    def __init__(self, hetero_graph: nx.MultiDiGraph, customer_graph: nx.Graph, datasets: Dict[str, pd.DataFrame]):
        self.H = hetero_graph
        self.G_cust = customer_graph
        self.datasets = datasets
        self.features_df: Optional[pd.DataFrame] = None

    def extract_features(self) -> pd.DataFrame:
        """Extracts complete feature matrix for all customer entities."""
        cust_df = self.datasets["customers"]
        txns_df = self.datasets["transactions"]
        ip_df = self.datasets["ip_addresses"].set_index("ip_id")["ip_type"].to_dict()

        customer_ids = cust_df["customer_id"].tolist()
        G_cust = self.G_cust

        # -------------------------------------------------------------
        # 1. GRAPH TOPOLOGY & CENTRALITY FEATURES
        # -------------------------------------------------------------
        # Degree & Weighted Degree in customer projection
        degrees = dict(G_cust.degree())
        weighted_degrees = dict(G_cust.degree(weight="weight"))

        active_nodes = [n for n, d in G_cust.degree() if d > 0]
        sub_g = G_cust.subgraph(active_nodes) if active_nodes else nx.Graph()

        # Clustering Coefficient (measures local density & triangular closure)
        clustering_coeffs = {cid: 0.0 for cid in customer_ids}
        if active_nodes:
            try:
                sub_cc = nx.clustering(sub_g)
                clustering_coeffs.update(sub_cc)
            except Exception:
                pass

        # PageRank (measures structural importance in resource-sharing network)
        pagerank_scores = {cid: 1.0 / len(customer_ids) for cid in customer_ids}
        if active_nodes:
            try:
                sub_pr = nx.pagerank(sub_g, weight="weight", max_iter=50, tol=1e-4)
                pagerank_scores.update(sub_pr)
            except Exception:
                pass

        # Betweenness Centrality (computed on active connected subgraph with k=100 sampling for fast execution)
        betweenness = {cid: 0.0 for cid in customer_ids}
        if active_nodes:
            try:
                k_sample = min(100, len(active_nodes))
                sub_betweenness = nx.betweenness_centrality(sub_g, weight="weight", k=k_sample, seed=42)
                betweenness.update(sub_betweenness)
            except Exception:
                pass

        # -------------------------------------------------------------
        # 2. BEHAVIORAL & RESOURCE-SHARING METRICS FROM TRANSACTIONS
        # -------------------------------------------------------------
        # Group transactions by customer
        txn_by_cust = txns_df.groupby("customer_id")
        
        # Pre-calculate global usage maps to quickly determine which devices/IPs/PMs are shared
        device_users = txns_df.groupby("device_id")["customer_id"].nunique()
        shared_devices_global = set(device_users[device_users > 1].index)

        ip_users = txns_df.groupby("ip_id")["customer_id"].nunique()
        shared_ips_global = set(ip_users[ip_users > 1].index)

        pm_users = txns_df.groupby("payment_method_id")["customer_id"].nunique()
        shared_pms_global = set(pm_users[pm_users > 1].index)

        # Datacenter / VPN IP set
        datacenter_vpn_ips = set(
            self.datasets["ip_addresses"][
                self.datasets["ip_addresses"]["ip_type"].isin(["DATACENTER", "VPN"])
            ]["ip_id"]
        )

        records = []
        for cid in customer_ids:
            # Graph topology
            deg = degrees.get(cid, 0)
            w_deg = round(weighted_degrees.get(cid, 0.0), 3)
            pr = round(pagerank_scores.get(cid, 0.0), 6)
            bc = round(betweenness.get(cid, 0.0), 6)
            cc = round(clustering_coeffs.get(cid, 0.0), 4)

            # Node degree in heterogeneous graph
            hetero_degree = self.H.degree(cid) if self.H.has_node(cid) else 0

            # Edge-specific shared resource details from G_cust neighbors
            shared_dev_count = 0
            shared_ip_count = 0
            shared_pm_count = 0
            shared_proxy_count = 0
            co_txn_count = 0

            if G_cust.has_node(cid):
                for nbr in G_cust.neighbors(cid):
                    edge_data = G_cust[cid][nbr]
                    shared_dev_count += edge_data.get("num_shared_devices", 0)
                    shared_ip_count += edge_data.get("num_shared_ips", 0)
                    shared_pm_count += edge_data.get("num_shared_pms", 0)
                    co_txn_count += edge_data.get("num_co_txns", 0)
                    
                    # Count datacenter/vpn shared IPs
                    for ip in edge_data.get("shared_ips", []):
                        if ip in datacenter_vpn_ips:
                            shared_proxy_count += 1

            # Transaction history metrics
            if cid in txn_by_cust.groups:
                c_txns = txn_by_cust.get_group(cid)
                txn_count = len(c_txns)
                total_volume = round(c_txns["amount"].sum(), 2)
                mean_amount = round(c_txns["amount"].mean(), 2)
                max_amount = round(c_txns["amount"].max(), 2)

                # Merchant concentration (HHI)
                merch_counts = Counter(c_txns["merchant_id"])
                total_merch_txns = len(c_txns)
                merch_hhi = round(sum((count / total_merch_txns) ** 2 for count in merch_counts.values()), 4)

                # Geographic spread
                unique_cities = c_txns["city"].nunique()

                # Temporal velocity & synchronization
                timestamps = pd.to_datetime(c_txns["timestamp"]).sort_values()
                time_span_days = max(1, (timestamps.max() - timestamps.min()).total_seconds() / 86400.0)
                txn_velocity_per_day = round(txn_count / time_span_days, 3)

                # Inter-arrival burstiness (std / mean of inter-transaction seconds)
                if len(timestamps) > 1:
                    deltas = timestamps.diff().dropna().dt.total_seconds()
                    min_delta_seconds = int(deltas.min())
                    # Bursts within 5 minutes (300s)
                    burst_count = int((deltas <= 300).sum())
                    sync_score = round(burst_count / len(deltas), 3)
                else:
                    min_delta_seconds = 86400
                    burst_count = 0
                    sync_score = 0.0

            else:
                txn_count = 0
                total_volume = 0.0
                mean_amount = 0.0
                max_amount = 0.0
                merch_hhi = 0.0
                unique_cities = 0
                txn_velocity_per_day = 0.0
                min_delta_seconds = 86400
                burst_count = 0
                sync_score = 0.0

            records.append({
                "customer_id": cid,
                "degree": deg,
                "weighted_degree": w_deg,
                "hetero_degree": hetero_degree,
                "pagerank": pr,
                "betweenness_centrality": bc,
                "clustering_coefficient": cc,
                "connected_customers": deg,
                "shared_device_count": shared_dev_count,
                "shared_ip_count": shared_ip_count,
                "shared_payment_count": shared_pm_count,
                "shared_proxy_count": shared_proxy_count,
                "co_transaction_count": co_txn_count,
                "transaction_count": txn_count,
                "transaction_volume": total_volume,
                "mean_amount": mean_amount,
                "max_amount": max_amount,
                "merchant_hhi": merch_hhi,
                "geographic_spread": unique_cities,
                "txn_velocity_per_day": txn_velocity_per_day,
                "min_inter_transaction_seconds": min_delta_seconds,
                "temporal_burst_count": burst_count,
                "temporal_sync_score": sync_score,
            })

        self.features_df = pd.DataFrame(records)
        return self.features_df
