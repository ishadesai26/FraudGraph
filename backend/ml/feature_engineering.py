"""Feature engineering engine for FraudGraph ML risk models.

Transforms raw transactions, customer demographics, and graph topological metrics
into featurized training matrices, strictly separating target labels from input features.
"""

from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import pandas as pd


class MLFeatureEngineer:
    """Builds transaction-level, behavioral, and graph-augmented feature matrices."""

    # Behavioral features used by the Baseline model (no graph features)
    BASELINE_NUMERICAL_FEATURES = [
        "amount",
        "amount_log",
        "hour_of_day",
        "time_of_day_sin",
        "time_of_day_cos",
        "day_of_week",
        "is_weekend",
        "customer_age",
        "account_age_days",
        "customer_txn_count",
        "customer_avg_amount",
        "customer_amount_std",
        "amount_deviation_ratio",
        "customer_merchant_count",
        "customer_device_count",
        "customer_ip_count",
        "customer_payment_method_count",
        "customer_velocity_per_day",
        "is_remote_city",
        "ip_is_proxy",
    ]

    BASELINE_CATEGORICAL_FEATURES = [
        "payment_type",
        "transaction_status",
    ]

    # Graph-derived features added to the FraudGraph model
    GRAPH_NUMERICAL_FEATURES = [
        "degree",
        "weighted_degree",
        "hetero_degree",
        "pagerank",
        "betweenness_centrality",
        "clustering_coefficient",
        "shared_device_count",
        "shared_ip_count",
        "shared_payment_count",
        "shared_proxy_count",
        "co_transaction_count",
        "merchant_hhi",
        "geographic_spread",
        "temporal_sync_score",
        "network_risk_score",
        "is_in_flagged_ring",
    ]

    def __init__(
        self,
        datasets: Dict[str, pd.DataFrame],
        graph_features_df: pd.DataFrame,
        rings_df: Optional[pd.DataFrame] = None,
        members_df: Optional[pd.DataFrame] = None,
    ):
        self.datasets = datasets
        self.graph_features_df = graph_features_df
        self.rings_df = rings_df
        self.members_df = members_df

    def build_feature_dataframe(self) -> pd.DataFrame:
        """Constructs the comprehensive feature DataFrame covering all transactions."""
        txns_df = self.datasets["transactions"].copy()
        cust_df = self.datasets["customers"].copy().set_index("customer_id")
        ip_df = self.datasets["ip_addresses"].copy().set_index("ip_id")

        # -------------------------------------------------------------
        # 1. TEMPORAL & TRANSACTION-LEVEL FEATURES
        # -------------------------------------------------------------
        txns_df["dt"] = pd.to_datetime(txns_df["timestamp"])
        txns_df["hour_of_day"] = txns_df["dt"].dt.hour
        txns_df["day_of_week"] = txns_df["dt"].dt.dayofweek
        txns_df["is_weekend"] = (txns_df["day_of_week"] >= 5).astype(int)

        # Cyclical temporal encodings
        txns_df["time_of_day_sin"] = np.sin(2 * np.pi * txns_df["hour_of_day"] / 24.0)
        txns_df["time_of_day_cos"] = np.cos(2 * np.pi * txns_df["hour_of_day"] / 24.0)

        # Log transform amount
        txns_df["amount"] = txns_df["amount"].astype(float)
        txns_df["amount_log"] = np.log1p(txns_df["amount"])

        # -------------------------------------------------------------
        # 2. CUSTOMER DEMOGRAPHICS & BEHAVIORAL AGGREGATES
        # -------------------------------------------------------------
        txns_df["customer_age"] = txns_df["customer_id"].map(cust_df["customer_age"]).fillna(35).astype(int)
        txns_df["account_age_days"] = txns_df["customer_id"].map(cust_df["account_age_days"]).fillna(180).astype(int)
        
        home_cities = cust_df["city"].to_dict()
        txns_df["home_city"] = txns_df["customer_id"].map(home_cities).fillna("Unknown")
        txns_df["is_remote_city"] = (txns_df["city"] != txns_df["home_city"]).astype(int)

        # IP Proxy Indicator
        ip_types = ip_df["ip_type"].to_dict()
        txns_df["ip_type"] = txns_df["ip_id"].map(ip_types).fillna("RESIDENTIAL")
        txns_df["ip_is_proxy"] = txns_df["ip_type"].isin(["DATACENTER", "VPN"]).astype(int)

        # Customer-level historical profiles
        cust_stats = txns_df.groupby("customer_id").agg(
            customer_txn_count=("transaction_id", "count"),
            customer_avg_amount=("amount", "mean"),
            customer_amount_std=("amount", "std"),
            customer_merchant_count=("merchant_id", "nunique"),
            customer_device_count=("device_id", "nunique"),
            customer_ip_count=("ip_id", "nunique"),
            customer_payment_method_count=("payment_method_id", "nunique"),
            min_ts=("dt", "min"),
            max_ts=("dt", "max"),
        )
        cust_stats["customer_amount_std"] = cust_stats["customer_amount_std"].fillna(0.0)

        # Active time span velocity
        time_spans = (cust_stats["max_ts"] - cust_stats["min_ts"]).dt.total_seconds() / 86400.0
        cust_stats["customer_velocity_per_day"] = cust_stats["customer_txn_count"] / np.maximum(1.0, time_spans)

        # Map customer aggregates onto transaction rows
        for col in [
            "customer_txn_count",
            "customer_avg_amount",
            "customer_amount_std",
            "customer_merchant_count",
            "customer_device_count",
            "customer_ip_count",
            "customer_payment_method_count",
            "customer_velocity_per_day",
        ]:
            txns_df[col] = txns_df["customer_id"].map(cust_stats[col]).fillna(0.0)

        # Relative deviation from customer's average spend
        txns_df["amount_deviation_ratio"] = (
            txns_df["amount"] - txns_df["customer_avg_amount"]
        ) / np.maximum(100.0, txns_df["customer_avg_amount"])

        # -------------------------------------------------------------
        # 3. GRAPH-DERIVED FEATURES INTEGRATION (From Phase 2)
        # -------------------------------------------------------------
        g_feat = self.graph_features_df.copy().set_index("customer_id")
        for col in [
            "degree",
            "weighted_degree",
            "hetero_degree",
            "pagerank",
            "betweenness_centrality",
            "clustering_coefficient",
            "shared_device_count",
            "shared_ip_count",
            "shared_payment_count",
            "shared_proxy_count",
            "co_transaction_count",
            "merchant_hhi",
            "geographic_spread",
            "temporal_sync_score",
        ]:
            if col in g_feat.columns:
                txns_df[col] = txns_df["customer_id"].map(g_feat[col]).fillna(0.0)
            else:
                txns_df[col] = 0.0

        # Network risk score & ring membership from ring detector
        if self.members_df is not None and not self.members_df.empty:
            mem_risk = self.members_df.groupby("customer_id")["network_risk_score"].max().to_dict()
            txns_df["network_risk_score"] = txns_df["customer_id"].map(mem_risk).fillna(0.0)
            txns_df["is_in_flagged_ring"] = (txns_df["network_risk_score"] >= 50.0).astype(int)
        else:
            txns_df["network_risk_score"] = 0.0
            txns_df["is_in_flagged_ring"] = 0

        # Ensure correct chronological order for time-aware splitting
        txns_df.sort_values(by="dt", inplace=True)
        txns_df.reset_index(drop=True, inplace=True)
        return txns_df

    def get_feature_splits(
        self,
        full_df: Optional[pd.DataFrame] = None,
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
    ) -> Dict[str, Any]:
        """Performs chronological time-aware train/validation/test split with strict label separation."""
        if full_df is None:
            full_df = self.build_feature_dataframe()

        # Target label extraction
        y = full_df["is_fraud"].values.astype(int)

        # Baseline features (behavioral only, no graph features)
        baseline_cols = self.BASELINE_NUMERICAL_FEATURES + self.BASELINE_CATEGORICAL_FEATURES
        X_baseline = full_df[baseline_cols].copy()

        # Graph-enhanced features (behavioral + graph features)
        graph_cols = baseline_cols + self.GRAPH_NUMERICAL_FEATURES
        X_graph = full_df[graph_cols].copy()

        n = len(full_df)
        train_end = int(n * train_ratio)
        val_end = int(n * (train_ratio + val_ratio))

        # Split indices
        train_idx = np.arange(0, train_end)
        val_idx = np.arange(train_end, val_end)
        test_idx = np.arange(val_end, n)

        return {
            "full_df": full_df,
            "feature_names_baseline": baseline_cols,
            "feature_names_graph": graph_cols,
            "baseline_numerical": self.BASELINE_NUMERICAL_FEATURES,
            "baseline_categorical": self.BASELINE_CATEGORICAL_FEATURES,
            "graph_numerical": self.BASELINE_NUMERICAL_FEATURES + self.GRAPH_NUMERICAL_FEATURES,
            "graph_categorical": self.BASELINE_CATEGORICAL_FEATURES,
            # Baseline feature splits
            "X_baseline_train": X_baseline.iloc[train_idx].copy(),
            "X_baseline_val": X_baseline.iloc[val_idx].copy(),
            "X_baseline_test": X_baseline.iloc[test_idx].copy(),
            # Graph feature splits
            "X_graph_train": X_graph.iloc[train_idx].copy(),
            "X_graph_val": X_graph.iloc[val_idx].copy(),
            "X_graph_test": X_graph.iloc[test_idx].copy(),
            # Labels
            "y_train": y[train_idx],
            "y_val": y[val_idx],
            "y_test": y[test_idx],
            # Meta slices for evaluation inspection
            "meta_train": full_df.iloc[train_idx][["transaction_id", "customer_id", "timestamp", "fraud_ring_id", "fraud_type"]].copy(),
            "meta_val": full_df.iloc[val_idx][["transaction_id", "customer_id", "timestamp", "fraud_ring_id", "fraud_type"]].copy(),
            "meta_test": full_df.iloc[test_idx][["transaction_id", "customer_id", "timestamp", "fraud_ring_id", "fraud_type"]].copy(),
        }
