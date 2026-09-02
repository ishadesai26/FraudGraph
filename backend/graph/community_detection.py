"""Community detection module for FraudGraph customer projection network.

Identifies densely connected clusters of customer accounts using Modularity Maximization
and Connected Component partitioning.
"""

from typing import Dict, List, Set, Tuple, Optional, Any
from collections import defaultdict
import networkx as nx
import pandas as pd


class CommunityDetector:
    """Detects and characterizes cohesive customer communities in the projection graph."""

    def __init__(self, customer_graph: nx.Graph, min_community_size: int = 2):
        """
        Algorithm: Louvain Multi-Level Modularity Maximization (Blondel et al.).
        
        Why Selected:
        1. High quality modularity optimization Q on large, weighted multi-relational graphs.
        2. Fast runtime complexity O(V * log V) compared to greedy modularity heaps.
        3. Deterministic and reproducible with fixed seed (seed=42).
        
        Limitations:
        - Resolution limit: Small cliques in very dense background networks may merge if inter-edge weights are non-zero.
        - Addressed in FraudGraph by combining modularity partitions with multi-signal subgraph density analysis.
        """
        self.G_cust = customer_graph
        self.min_community_size = min_community_size
        self.communities: List[Dict[str, Any]] = []

    def detect_communities(self) -> List[Dict[str, Any]]:
        """Executes community detection and extracts structural community metrics."""
        G = self.G_cust

        # Filter to only connected nodes (degree >= 1)
        active_nodes = [n for n, d in G.degree() if d > 0]
        if not active_nodes:
            return []

        subgraph = G.subgraph(active_nodes)

        # Detect communities using Louvain modularity optimization (deterministic seed)
        try:
            raw_communities = list(nx.community.louvain_communities(subgraph, weight="weight", seed=42))
        except Exception:
            # Fallback to connected components if Louvain is unavailable
            raw_communities = list(nx.connected_components(subgraph))

        community_records = []
        for idx, member_set in enumerate(raw_communities, start=1):
            members = list(member_set)
            if len(members) < self.min_community_size:
                continue

            comm_subgraph = G.subgraph(members)
            comm_id = f"COMM_{idx:03d}"

            # Structural topology metrics
            num_nodes = len(members)
            num_edges = comm_subgraph.number_of_edges()
            density = round(nx.density(comm_subgraph), 4) if num_nodes > 1 else 0.0

            # Sum of internal weighted connections
            internal_weight = round(sum(d.get("weight", 1.0) for _, _, d in comm_subgraph.edges(data=True)), 2)

            # Aggregate shared resource footprints inside the community
            shared_devices: Set[str] = set()
            shared_ips: Set[str] = set()
            shared_pms: Set[str] = set()
            co_txns_total = 0

            for _, _, edge_data in comm_subgraph.edges(data=True):
                shared_devices.update(edge_data.get("shared_devices", []))
                shared_ips.update(edge_data.get("shared_ips", []))
                shared_pms.update(edge_data.get("shared_pms", []))
                co_txns_total += edge_data.get("num_co_txns", 0)

            community_records.append({
                "community_id": comm_id,
                "members": members,
                "customer_count": num_nodes,
                "edge_count": num_edges,
                "density": density,
                "internal_weight": internal_weight,
                "shared_devices": list(shared_devices),
                "shared_ips": list(shared_ips),
                "shared_pms": list(shared_pms),
                "shared_device_count": len(shared_devices),
                "shared_ip_count": len(shared_ips),
                "shared_payment_count": len(shared_pms),
                "co_transaction_count": co_txns_total,
            })

        self.communities = community_records
        return self.communities
