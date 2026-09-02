"""Ground-truth evaluation module for FraudGraph detector benchmarking.

Evaluates the graph detection engine against Phase 1 ground-truth annotations:
- Ring Detection Rate
- Customer-level Precision, Recall, F1 Score
- Transaction-level Precision, Recall, F1 Score
- False Positive Analysis
"""

from typing import Dict, List, Set, Tuple, Optional, Any
import pandas as pd
import numpy as np


class GroundTruthEvaluator:
    """Evaluates graph-detected fraud rings against ground-truth labels."""

    def __init__(self, rings_df: pd.DataFrame, members_df: pd.DataFrame, datasets: Dict[str, pd.DataFrame]):
        self.rings_df = rings_df
        self.members_df = members_df
        self.datasets = datasets

    def evaluate(self) -> Dict[str, Any]:
        """Calculates exact evaluation metrics."""
        txns_df = self.datasets["transactions"]
        cust_df = self.datasets["customers"]

        # -------------------------------------------------------------
        # 1. GROUND TRUTH DEFINITIONS
        # -------------------------------------------------------------
        # Fraud transactions & fraud customers from ground truth
        gt_fraud_txns = txns_df[txns_df["is_fraud"] == 1]
        gt_fraud_cust_ids = set(gt_fraud_txns["customer_id"].unique())
        gt_legit_cust_ids = set(cust_df["customer_id"].unique()) - gt_fraud_cust_ids

        gt_rings = [r for r in gt_fraud_txns["fraud_ring_id"].dropna().unique() if str(r).strip() != ""]
        total_gt_rings = len(gt_rings)

        # -------------------------------------------------------------
        # 2. DETECTED PREDICTIONS
        # -------------------------------------------------------------
        if self.members_df is not None and not self.members_df.empty:
            pred_fraud_cust_ids = set(self.members_df["customer_id"].unique())
            pred_fraud_txns = txns_df[txns_df["customer_id"].isin(pred_fraud_cust_ids)]
            pred_fraud_txn_ids = set(pred_fraud_txns["transaction_id"])
        else:
            pred_fraud_cust_ids = set()
            pred_fraud_txn_ids = set()

        # -------------------------------------------------------------
        # 3. RING-LEVEL DETECTION RATE
        # -------------------------------------------------------------
        # A ground truth ring is considered detected if >= 50% of its members are captured in detected rings
        detected_gt_rings = 0
        ring_breakdown = {}

        for ring_id in gt_rings:
            ring_members = set(gt_fraud_txns[gt_fraud_txns["fraud_ring_id"] == ring_id]["customer_id"].unique())
            captured = ring_members.intersection(pred_fraud_cust_ids)
            capture_rate = len(captured) / max(1, len(ring_members))
            is_detected = capture_rate >= 0.50
            if is_detected:
                detected_gt_rings += 1

            ring_breakdown[ring_id] = {
                "total_members": len(ring_members),
                "captured_members": len(captured),
                "capture_rate": round(capture_rate, 3),
                "is_detected": is_detected,
            }

        ring_detection_rate = round(detected_gt_rings / max(1, total_gt_rings) * 100, 2)

        # -------------------------------------------------------------
        # 4. CUSTOMER-LEVEL METRICS (Precision, Recall, F1)
        # -------------------------------------------------------------
        tp_cust = len(pred_fraud_cust_ids.intersection(gt_fraud_cust_ids))
        fp_cust = len(pred_fraud_cust_ids.intersection(gt_legit_cust_ids))
        fn_cust = len(gt_fraud_cust_ids - pred_fraud_cust_ids)
        tn_cust = len(gt_legit_cust_ids - pred_fraud_cust_ids)

        cust_precision = round(tp_cust / max(1, tp_cust + fp_cust) * 100, 2)
        cust_recall = round(tp_cust / max(1, tp_cust + fn_cust) * 100, 2)
        if cust_precision + cust_recall > 0:
            cust_f1 = round(2 * (cust_precision * cust_recall) / (cust_precision + cust_recall), 2)
        else:
            cust_f1 = 0.0

        # -------------------------------------------------------------
        # 5. TRANSACTION-LEVEL METRICS
        # -------------------------------------------------------------
        gt_fraud_txn_ids = set(gt_fraud_txns["transaction_id"])
        gt_legit_txn_ids = set(txns_df[txns_df["is_fraud"] == 0]["transaction_id"])

        tp_txn = len(pred_fraud_txn_ids.intersection(gt_fraud_txn_ids))
        fp_txn = len(pred_fraud_txn_ids.intersection(gt_legit_txn_ids))
        fn_txn = len(gt_fraud_txn_ids - pred_fraud_txn_ids)

        txn_precision = round(tp_txn / max(1, tp_txn + fp_txn) * 100, 2)
        txn_recall = round(tp_txn / max(1, tp_txn + fn_txn) * 100, 2)
        if txn_precision + txn_recall > 0:
            txn_f1 = round(2 * (txn_precision * txn_recall) / (txn_precision + txn_recall), 2)
        else:
            txn_f1 = 0.0

        return {
            "total_gt_rings": total_gt_rings,
            "detected_gt_rings": detected_gt_rings,
            "ring_detection_rate_pct": ring_detection_rate,
            "ring_breakdown": ring_breakdown,
            "customer_metrics": {
                "true_positives": tp_cust,
                "false_positives": fp_cust,
                "false_negatives": fn_cust,
                "true_negatives": tn_cust,
                "precision_pct": cust_precision,
                "recall_pct": cust_recall,
                "f1_score": cust_f1,
            },
            "transaction_metrics": {
                "true_positives": tp_txn,
                "false_positives": fp_txn,
                "false_negatives": fn_txn,
                "precision_pct": txn_precision,
                "recall_pct": txn_recall,
                "f1_score": txn_f1,
            },
        }
