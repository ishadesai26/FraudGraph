"""Feature-level explanation engine for FraudGraph.

Analyzes transaction behavioral attributes, historical customer profiles, and ML model
feature importances to identify contributing risk factors and protective signals.
"""

from typing import Dict, List, Optional, Any, Tuple
import numpy as np
import pandas as pd


class FeatureExplainer:
    """Extracts feature-level risk attributions and protective factors."""

    def __init__(
        self,
        feature_importance_data: Optional[Dict[str, Any]] = None,
    ):
        self.feature_importance_data = feature_importance_data or {}
        self._feat_imp_map: Dict[str, float] = {}
        
        if "fraudgraph_features" in self.feature_importance_data:
            for item in self.feature_importance_data["fraudgraph_features"]:
                self._feat_imp_map[item["feature"]] = float(item.get("importance", 0.0))

    def explain_transaction_features(
        self,
        txn_row: pd.Series,
        cust_row: Optional[pd.Series] = None,
        anomaly_score: Optional[float] = None,
        model_prob: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Analyzes a single transaction event for behavioral risk and protective signals."""
        risk_signals = []
        protective_signals = []

        amount = float(txn_row.get("amount", 0.0))
        cust_avg = float(txn_row.get("customer_avg_amount", amount))
        velocity = float(txn_row.get("customer_velocity_per_day", 0.0))
        is_remote = int(txn_row.get("is_remote_city", 0))
        ip_is_proxy = int(txn_row.get("ip_is_proxy", 0))
        hour = int(txn_row.get("hour_of_day", 12))
        account_age = int(txn_row.get("account_age_days", 180))

        # 1. Amount Spikes & Deviation
        if cust_avg > 0 and amount > 3.0 * cust_avg and amount > 10000:
            ratio = round(amount / cust_avg, 1)
            risk_signals.append({
                "signal": "amount_spike",
                "feature": "amount_deviation_ratio",
                "severity": "HIGH" if amount > 30000 else "MEDIUM",
                "value": f"₹{amount:,.2f}",
                "baseline": f"Customer Avg: ₹{cust_avg:,.2f} ({ratio}x normal)",
                "importance": self._feat_imp_map.get("amount_deviation_ratio", 0.08),
                "type": "RISK_SIGNAL",
                "description": f"Transaction amount of ₹{amount:,.2f} is {ratio}x higher than customer's historical average of ₹{cust_avg:,.2f}.",
            })
        elif amount <= 1.5 * cust_avg and amount < 15000:
            protective_signals.append({
                "signal": "consistent_amount",
                "feature": "amount",
                "severity": "LOW",
                "value": f"₹{amount:,.2f}",
                "baseline": f"Customer Avg: ₹{cust_avg:,.2f}",
                "importance": 0.05,
                "type": "PROTECTIVE_SIGNAL",
                "description": f"Transaction amount of ₹{amount:,.2f} aligns with customer's typical spending patterns.",
            })

        # 2. Transaction Velocity Spikes
        if velocity > 3.0:
            risk_signals.append({
                "signal": "elevated_velocity",
                "feature": "customer_velocity_per_day",
                "severity": "HIGH" if velocity > 6.0 else "MEDIUM",
                "value": f"{velocity:.1f} txns/day",
                "baseline": "Normal Velocity: < 1.5 txns/day",
                "importance": self._feat_imp_map.get("customer_velocity_per_day", 0.07),
                "type": "RISK_SIGNAL",
                "description": f"Customer transaction velocity of {velocity:.1f} transactions/day indicates rapid successive payments.",
            })

        # 3. Proxy / Datacenter IP Routing
        if ip_is_proxy:
            risk_signals.append({
                "signal": "proxy_ip_routing",
                "feature": "ip_is_proxy",
                "severity": "HIGH",
                "value": "DATACENTER / VPN IP",
                "baseline": "Legitimate Gateway: RESIDENTIAL",
                "importance": self._feat_imp_map.get("ip_is_proxy", 0.06),
                "type": "RISK_SIGNAL",
                "description": "Transaction originated from a known Datacenter or VPN proxy network, masking user physical origin.",
            })

        # 4. Remote City Transaction
        if is_remote:
            home_c = txn_row.get("home_city", "Home City")
            txn_c = txn_row.get("city", "Remote City")
            risk_signals.append({
                "signal": "geographic_deviation",
                "feature": "is_remote_city",
                "severity": "MEDIUM",
                "value": f"{txn_c} (Registered Home: {home_c})",
                "baseline": f"Registered City: {home_c}",
                "importance": self._feat_imp_map.get("is_remote_city", 0.04),
                "type": "RISK_SIGNAL",
                "description": f"Transaction initiated in {txn_c}, which differs from customer's registered primary location ({home_c}).",
            })

        # 5. Unusual Off-Hours Activity (2 AM - 5 AM)
        if hour in [2, 3, 4, 5]:
            risk_signals.append({
                "signal": "unusual_timing",
                "feature": "hour_of_day",
                "severity": "LOW",
                "value": f"{hour:02d}:00 HRS",
                "baseline": "Standard Trading Hours: 08:00 - 22:00 HRS",
                "importance": self._feat_imp_map.get("hour_of_day", 0.03),
                "type": "RISK_SIGNAL",
                "description": f"Transaction executed during abnormal off-peak overnight hours ({hour:02d}:00 HRS).",
            })

        # 6. Protective: Mature Account History
        if account_age > 180:
            protective_signals.append({
                "signal": "mature_account",
                "feature": "account_age_days",
                "severity": "LOW",
                "value": f"{account_age} days",
                "baseline": "New Account Threshold: < 30 days",
                "importance": 0.06,
                "type": "PROTECTIVE_SIGNAL",
                "description": f"Account has an established tenure of {account_age} days with historical legitimate activity.",
            })

        # 7. ML Model Probability & Anomaly Score
        if model_prob is not None and model_prob >= 0.50:
            risk_signals.append({
                "signal": "supervised_model_risk",
                "feature": "model_probability",
                "severity": "CRITICAL" if model_prob >= 0.80 else "HIGH",
                "value": f"{model_prob * 100:.1f}%",
                "baseline": "Classification Decision Threshold: 50.0%",
                "importance": 0.35,
                "type": "RISK_SIGNAL",
                "description": f"Supervised RandomForest fraud classifier estimated a {model_prob * 100:.1f}% fraud probability.",
            })

        if anomaly_score is not None and anomaly_score >= 60.0:
            risk_signals.append({
                "signal": "behavioral_anomaly_score",
                "feature": "anomaly_score",
                "severity": "HIGH" if anomaly_score >= 80.0 else "MEDIUM",
                "value": f"{anomaly_score:.1f}/100",
                "baseline": "Normal Anomaly Threshold: < 50/100",
                "importance": 0.20,
                "type": "RISK_SIGNAL",
                "description": f"Unsupervised IsolationForest flagged multi-dimensional behavioral deviation (Score: {anomaly_score:.1f}/100).",
            })

        return {
            "risk_signals": sorted(risk_signals, key=lambda x: x["importance"], reverse=True),
            "protective_signals": protective_signals,
            "total_risk_signals": len(risk_signals),
            "total_protective_signals": len(protective_signals),
        }
