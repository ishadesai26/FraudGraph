"""Coordinated fraud-ring detection and network risk scoring engine."""

from typing import Dict, List, Set, Tuple, Optional, Any
from collections import Counter
import pandas as pd
import numpy as np

from backend.graph.community_detection import CommunityDetector


class FraudRingDetector:
    """Calculates individual vs network risk and extracts coordinated fraud rings."""

    def __init__(
        self,
        features_df: pd.DataFrame,
        communities: List[Dict[str, Any]],
        datasets: Dict[str, pd.DataFrame],
        risk_threshold: float = 50.0,
    ):
        self.features_df = features_df.set_index("customer_id")
        self.communities = communities
        self.datasets = datasets
        self.risk_threshold = risk_threshold

        self.rings_df: Optional[pd.DataFrame] = None
        self.members_df: Optional[pd.DataFrame] = None
        self.customer_risk_df: Optional[pd.DataFrame] = None

    def calculate_individual_risk(self) -> pd.DataFrame:
        """Calculates network-independent individual risk for each customer."""
        df = self.features_df.copy()

        # 1. Velocity component (0 - 25)
        vel_score = np.clip((df["txn_velocity_per_day"] / 1.5) * 25.0, 0, 25.0)

        # 2. Volume / Ticket size component (0 - 25)
        vol_score = np.clip((df["mean_amount"] / 35000.0) * 25.0, 0, 25.0)

        # 3. Merchant concentration component (0 - 25)
        hhi_score = np.clip(df["merchant_hhi"] * 25.0, 0, 25.0)

        # 4. Temporal burst component (0 - 25)
        burst_score = np.clip(df["temporal_sync_score"] * 25.0, 0, 25.0)

        ind_score = np.clip(vel_score + vol_score + hhi_score + burst_score, 0.0, 100.0)
        df["individual_risk_score"] = ind_score.round(2)
        return df

    def detect_fraud_rings(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Evaluates detected communities and scores coordinated network risk."""
        txns_df = self.datasets["transactions"]
        ip_df = self.datasets["ip_addresses"].set_index("ip_id")["ip_type"].to_dict()

        ind_df = self.calculate_individual_risk()

        rings_records = []
        members_records = []
        ring_counter = 1

        for comm in self.communities:
            members = comm["members"]
            num_members = len(members)
            if num_members < 2:
                continue

            # Community transaction slices
            comm_txns = txns_df[txns_df["customer_id"].isin(members)]
            total_txns = len(comm_txns)
            total_vol = round(comm_txns["amount"].sum(), 2) if total_txns > 0 else 0.0

            # Distinct resources
            num_devs = comm["shared_device_count"]
            num_ips = comm["shared_ip_count"]
            num_pms = comm["shared_payment_count"]
            co_txns = comm.get("co_transaction_count", 0)

            # Check if any shared IP is DATACENTER / VPN
            proxy_ips = [ip for ip in comm["shared_ips"] if ip_df.get(ip) in ["DATACENTER", "VPN"]]
            num_proxy_ips = len(proxy_ips)

            # Community merchant concentration
            if total_txns > 0:
                merch_counts = Counter(comm_txns["merchant_id"])
                merch_hhi = sum((c / total_txns) ** 2 for c in merch_counts.values())
                unique_merchs = len(merch_counts)
                unique_cities = comm_txns["city"].nunique()
            else:
                merch_hhi = 0.0
                unique_merchs = 0
                unique_cities = 0

            # Average temporal synchronization across members
            member_features = ind_df.loc[ind_df.index.isin(members)]
            avg_sync = member_features["temporal_sync_score"].mean() if not member_features.empty else 0.0

            # ---------------------------------------------------------
            # INDEPENDENT SIGNAL SCORING (Deterministic formula)
            # ---------------------------------------------------------
            signals_present = []
            raw_score = 0.0

            # Signal 1: Shared Device Farm (0 - 30)
            if num_devs > 0:
                dev_ratio = num_members / max(1, num_devs)
                sig_dev = min(30.0, dev_ratio * 10.0)
                raw_score += sig_dev
                signals_present.append(f"shared_devices({num_devs})")

            # Signal 2: Shared Payment Instruments (0 - 35)
            if num_pms > 0:
                pm_ratio = num_members / max(1, num_pms)
                sig_pm = min(35.0, pm_ratio * 12.0)
                raw_score += sig_pm
                signals_present.append(f"shared_payment_instruments({num_pms})")

            # Signal 3: Shared Proxy / IP (0 - 20)
            if num_ips > 0:
                if num_proxy_ips > 0:
                    sig_ip = min(20.0, 10.0 + (num_members / max(1, num_proxy_ips)) * 4.0)
                    signals_present.append(f"shared_datacenter_vpn({num_proxy_ips})")
                else:
                    # Legitimate residential shared IP gives minor baseline
                    sig_ip = min(6.0, 1.5 * num_ips)
                    signals_present.append(f"shared_residential_ip({num_ips})")
                raw_score += sig_ip

            # Signal 4: Coordinated Timing & Burst Synchronicity (0 - 25)
            if avg_sync > 0.15 or co_txns > 0:
                sig_sync = min(25.0, avg_sync * 20.0 + min(10.0, co_txns * 1.5))
                raw_score += sig_sync
                signals_present.append(f"synchronized_timing(sync={avg_sync:.2f},co_tx={co_txns})")

            # Signal 5: Merchant Concentration / Targeting (0 - 20)
            if merch_hhi > 0.40 and total_txns >= 10:
                sig_merch = min(20.0, merch_hhi * 20.0)
                raw_score += sig_merch
                signals_present.append(f"merchant_targeting(hhi={merch_hhi:.2f})")

            # Signal 6: Community Structural Density (0 - 15)
            density = comm["density"]
            if density > 0.30:
                sig_dense = min(15.0, density * 15.0)
                raw_score += sig_dense
                signals_present.append(f"high_subgraph_density({density:.2f})")

            # Signal 7: Elevated Transaction Volume (0 - 15)
            avg_txn_amt = total_vol / max(1, total_txns)
            if avg_txn_amt > 15000.0:
                sig_vol = min(15.0, (avg_txn_amt / 45000.0) * 15.0)
                raw_score += sig_vol
                signals_present.append(f"elevated_ticket_volume(avg=₹{avg_txn_amt:,.0f})")

            # ---------------------------------------------------------
            # MULTI-SIGNAL SYNERGY COMPOUNDING (Prevents single-signal false positives)
            # ---------------------------------------------------------
            num_active_signals = len(signals_present)
            if num_active_signals == 0:
                multiplier = 0.0
            elif num_active_signals == 1:
                # Single isolated signal (e.g. only shared residential IP): heavily penalized
                multiplier = 0.35
            elif num_active_signals == 2:
                multiplier = 0.70
            elif num_active_signals == 3:
                multiplier = 1.00
            else:
                # Synergy amplification for multi-vector organized syndicates
                multiplier = 1.00 + 0.12 * (num_active_signals - 3)

            final_network_risk = round(min(100.0, max(0.0, raw_score * multiplier)), 2)

            # Classify as suspicious Fraud Ring if network risk exceeds threshold
            if final_network_risk >= self.risk_threshold:
                ring_id = f"FR_{ring_counter:03d}"
                ring_counter += 1

                rings_records.append({
                    "ring_id": ring_id,
                    "risk_score": final_network_risk,
                    "customer_count": num_members,
                    "transaction_count": total_txns,
                    "transaction_volume": total_vol,
                    "shared_device_count": num_devs,
                    "shared_ip_count": num_ips,
                    "shared_payment_count": num_pms,
                    "merchant_count": unique_merchs,
                    "geographic_spread": unique_cities,
                    "time_synchronization_score": round(avg_sync, 3),
                    "risk_signals": "; ".join(signals_present),
                })

                # Member records with individual vs network risk
                # Identify core member based on highest degree in community
                max_deg = member_features["degree"].max() if not member_features.empty else 0
                for cid in members:
                    ind_score_val = ind_df.loc[cid, "individual_risk_score"] if cid in ind_df.index else 0.0
                    is_core = (ind_df.loc[cid, "degree"] == max_deg) if cid in ind_df.index else False
                    members_records.append({
                        "ring_id": ring_id,
                        "customer_id": cid,
                        "individual_risk_score": ind_score_val,
                        "network_risk_score": final_network_risk,
                        "is_core_member": is_core,
                    })

        self.rings_df = pd.DataFrame(rings_records)
        if not self.rings_df.empty:
            self.rings_df.sort_values(by="risk_score", ascending=False, inplace=True)

        self.members_df = pd.DataFrame(members_records)
        self.customer_risk_df = ind_df.reset_index()
        return self.rings_df, self.members_df
