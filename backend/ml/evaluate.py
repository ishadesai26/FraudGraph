"""Evaluation and comparative benchmarking pipeline for FraudGraph ML models.

Executes:
1. Loads trained artifacts from backend/ml/artifacts/
2. Computes test-set predictions for Baseline and FraudGraph models
3. Calculates Precision, Recall, F1, ROC-AUC, FPR, and Confusion Matrices
4. Performs Multi-Threshold Tradeoff Analysis
5. Exports data/processed/model_metrics.json
6. Generates evaluation visual plots under data/processed/evaluation/
"""

import sys
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Non-interactive headless backend
import matplotlib.pyplot as plt
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    roc_curve,
    precision_recall_curve,
    confusion_matrix,
    auc,
)

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.config.settings import get_settings
from backend.graph.graph_builder import GraphBuilder
from backend.graph.graph_features import GraphFeatureExtractor
from backend.graph.ring_detector import FraudRingDetector
from backend.graph.community_detection import CommunityDetector
from backend.ml.feature_engineering import MLFeatureEngineer
from backend.ml.preprocessing import DataPreprocessor
from backend.ml.baseline_model import BaselineFraudModel
from backend.ml.anomaly_detector import AnomalyDetector
from backend.ml.graph_model import FraudGraphModel
from backend.ml.risk_scorer import CompositeRiskScorer


def calculate_metrics_at_threshold(y_true: np.ndarray, y_proba: np.ndarray, threshold: float = 0.5) -> dict:
    """Calculates precision, recall, f1, fpr, and confusion matrix at a specific threshold."""
    y_pred = (y_proba >= threshold).astype(int)

    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    fpr = fp / max(1, fp + tn)

    return {
        "threshold": round(threshold, 2),
        "precision": round(float(prec), 4),
        "recall": round(float(rec), 4),
        "f1": round(float(f1), 4),
        "false_positive_rate": round(float(fpr), 4),
        "confusion_matrix": {
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "true_positives": int(tp),
        },
    }


def evaluate_models() -> dict:
    """Evaluates Baseline vs FraudGraph models on held-out test data."""
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    settings = get_settings()
    artifacts_dir = Path(__file__).resolve().parent / "artifacts"
    processed_dir = settings.processed_data_dir
    eval_plot_dir = processed_dir / "evaluation"
    eval_plot_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("FRAUDGRAPH PHASE 3: MODEL EVALUATION & BENCHMARKING")
    print("=" * 60)

    # 1. Load trained artifacts
    print("\n[1/5] Loading Trained Model Artifacts...")
    prep_baseline = DataPreprocessor.load(str(artifacts_dir / "preprocessor_baseline.joblib"))
    prep_graph = DataPreprocessor.load(str(artifacts_dir / "preprocessor_graph.joblib"))
    baseline_model = BaselineFraudModel.load(str(artifacts_dir / "baseline_model.joblib"))
    anomaly_detector = AnomalyDetector.load(str(artifacts_dir / "anomaly_model.joblib"))
    fraudgraph_model = FraudGraphModel.load(str(artifacts_dir / "fraudgraph_model.joblib"))

    # 2. Build test dataset
    print("\n[2/5] Preparing Held-Out Test Split...")
    builder = GraphBuilder(data_dir=settings.raw_data_dir)
    datasets = builder.load_datasets()
    H = builder.build_heterogeneous_graph(datasets)
    G_cust = builder.build_customer_projection_graph(datasets)
    extractor = GraphFeatureExtractor(H, G_cust, datasets)
    graph_features_df = extractor.extract_features()

    detector = CommunityDetector(G_cust, min_community_size=2)
    communities = detector.detect_communities()
    ring_detector = FraudRingDetector(
        features_df=graph_features_df,
        communities=communities,
        datasets=datasets,
        risk_threshold=50.0,
    )
    rings_df, members_df = ring_detector.detect_fraud_rings()

    feat_engineer = MLFeatureEngineer(
        datasets=datasets,
        graph_features_df=graph_features_df,
        rings_df=rings_df,
        members_df=members_df,
    )
    splits = feat_engineer.get_feature_splits(train_ratio=0.70, val_ratio=0.15, test_ratio=0.15)

    y_test = splits["y_test"]
    X_base_test_prep = prep_baseline.transform(splits["X_baseline_test"])
    X_graph_test_prep = prep_graph.transform(splits["X_graph_test"])

    print(f"  Test Set Size: {len(y_test):,} transactions (Ground Truth Fraud: {y_test.sum()})")

    # 3. Generate test probabilities
    print("\n[3/5] Generating Model Inferences on Test Set...")
    base_probs = baseline_model.predict_proba(X_base_test_prep)
    graph_probs = fraudgraph_model.predict_proba(X_graph_test_prep)
    anomaly_scores = anomaly_detector.predict_anomaly_score(X_base_test_prep)

    # Calculate ROC-AUC
    base_auc = round(float(roc_auc_score(y_test, base_probs)), 4)
    graph_auc = round(float(roc_auc_score(y_test, graph_probs)), 4)

    # Standard threshold (0.50) metrics
    base_m50 = calculate_metrics_at_threshold(y_test, base_probs, threshold=0.50)
    graph_m50 = calculate_metrics_at_threshold(y_test, graph_probs, threshold=0.50)

    base_m50["roc_auc"] = base_auc
    graph_m50["roc_auc"] = graph_auc

    # 4. Multi-threshold sweep analysis
    print("\n[4/5] Running Multi-Threshold Tradeoff Analysis...")
    thresholds = [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90]
    base_threshold_sweep = [calculate_metrics_at_threshold(y_test, base_probs, t) for t in thresholds]
    graph_threshold_sweep = [calculate_metrics_at_threshold(y_test, graph_probs, t) for t in thresholds]

    # Find optimal F1 threshold for each model
    best_base_thresh = max(base_threshold_sweep, key=lambda x: x["f1"])
    best_graph_thresh = max(graph_threshold_sweep, key=lambda x: x["f1"])

    # Composite risk scoring test evaluation
    scorer = CompositeRiskScorer()
    test_net_risks = splits["X_graph_test"]["network_risk_score"].values
    scored_test_df = scorer.score_batch(
        model_probs=graph_probs,
        network_risks=test_net_risks,
        anomaly_scores=anomaly_scores,
    )
    risk_level_counts = scored_test_df["risk_level"].value_counts().to_dict()

    # 5. Export JSON metrics & Generate Plots
    print("\n[5/5] Generating Visual Evaluation Artifacts & Exporting Metrics...")
    metrics_data = {
        "test_sample_count": len(y_test),
        "test_fraud_count": int(y_test.sum()),
        "baseline_model": {
            "model_type": "RandomForestClassifier",
            "features_used": "Transaction + Customer Behavioral (No Graph)",
            "roc_auc": base_auc,
            "metrics_at_default_threshold_0.50": base_m50,
            "optimal_threshold_profile": best_base_thresh,
            "threshold_sweep": base_threshold_sweep,
        },
        "fraudgraph_model": {
            "model_type": "RandomForestClassifier",
            "features_used": "Behavioral + Graph Network Relational",
            "roc_auc": graph_auc,
            "metrics_at_default_threshold_0.50": graph_m50,
            "optimal_threshold_profile": best_graph_thresh,
            "threshold_sweep": graph_threshold_sweep,
        },
        "anomaly_detector": {
            "model_type": "IsolationForest",
            "mean_anomaly_score": round(float(anomaly_scores.mean()), 2),
            "max_anomaly_score": round(float(anomaly_scores.max()), 2),
        },
        "composite_risk_distribution": risk_level_counts,
    }

    metrics_path = processed_dir / "model_metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics_data, f, indent=2)
    print(f"  Saved: {metrics_path.name}")

    # Generate Plot 1: ROC Curves
    plt.figure(figsize=(7, 6))
    fpr_b, tpr_b, _ = roc_curve(y_test, base_probs)
    fpr_g, tpr_g, _ = roc_curve(y_test, graph_probs)
    plt.plot(fpr_b, tpr_b, label=f"Baseline Model (AUC = {base_auc:.3f})", color="#2b5c8f", lw=2)
    plt.plot(fpr_g, tpr_g, label=f"FraudGraph Model (AUC = {graph_auc:.3f})", color="#c93b2b", lw=2)
    plt.plot([0, 1], [0, 1], linestyle="--", color="grey", alpha=0.7)
    plt.xlabel("False Positive Rate (FPR)", fontsize=11)
    plt.ylabel("True Positive Rate (Recall)", fontsize=11)
    plt.title("ROC Curves: Baseline vs FraudGraph Model", fontsize=12, fontweight="bold")
    plt.legend(loc="lower right", fontsize=10)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.tight_layout()
    plt.savefig(eval_plot_dir / "roc_curves.png", dpi=150)
    plt.close()

    # Generate Plot 2: Precision-Recall Curves
    plt.figure(figsize=(7, 6))
    p_b, r_b, _ = precision_recall_curve(y_test, base_probs)
    p_g, r_g, _ = precision_recall_curve(y_test, graph_probs)
    pr_auc_b = auc(r_b, p_b)
    pr_auc_g = auc(r_g, p_g)
    plt.plot(r_b, p_b, label=f"Baseline Model (PR-AUC = {pr_auc_b:.3f})", color="#2b5c8f", lw=2)
    plt.plot(r_g, p_g, label=f"FraudGraph Model (PR-AUC = {pr_auc_g:.3f})", color="#c93b2b", lw=2)
    plt.xlabel("Recall", fontsize=11)
    plt.ylabel("Precision", fontsize=11)
    plt.title("Precision-Recall Curves: Baseline vs FraudGraph", fontsize=12, fontweight="bold")
    plt.legend(loc="upper right", fontsize=10)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.tight_layout()
    plt.savefig(eval_plot_dir / "pr_curves.png", dpi=150)
    plt.close()

    # Generate Plot 3: Confusion Matrices Comparison
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    cm_b = confusion_matrix(y_test, (base_probs >= best_base_thresh["threshold"]).astype(int))
    cm_g = confusion_matrix(y_test, (graph_probs >= best_graph_thresh["threshold"]).astype(int))

    for ax, cm, title, color in [
        (axes[0], cm_b, f"Baseline (Thresh={best_base_thresh['threshold']})", "Blues"),
        (axes[1], cm_g, f"FraudGraph (Thresh={best_graph_thresh['threshold']})", "Greens"),
    ]:
        im = ax.imshow(cm, cmap=color, interpolation="nearest")
        ax.set_title(title, fontsize=11, fontweight="bold")
        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(["Legitimate", "Fraud"])
        ax.set_yticklabels(["Legitimate", "Fraud"])
        ax.set_xlabel("Predicted Label")
        ax.set_ylabel("True Label")
        for i in range(2):
            for j in range(2):
                ax.text(j, i, f"{cm[i, j]:,}", ha="center", va="center", color="black" if cm[i, j] < cm.max()/2 else "white", fontsize=12, fontweight="bold")
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    plt.tight_layout()
    plt.savefig(eval_plot_dir / "confusion_matrices.png", dpi=150)
    plt.close()

    # Generate Plot 4: Top Feature Importances (FraudGraph Model)
    graph_imp_df = fraudgraph_model.get_feature_importance().head(15)
    plt.figure(figsize=(9, 5.5))
    colors = ["#c93b2b" if cat == "graph_relational" else "#2b5c8f" for cat in graph_imp_df["category"]]
    plt.barh(graph_imp_df["feature"][::-1], graph_imp_df["importance"][::-1], color=colors[::-1])
    plt.xlabel("Gini Feature Importance", fontsize=11)
    plt.title("Top 15 Predictive Features in FraudGraph Model", fontsize=12, fontweight="bold")
    
    # Legend
    legend_elements = [
        plt.Rectangle((0, 0), 1, 1, color="#c93b2b", label="Graph Relational Feature"),
        plt.Rectangle((0, 0), 1, 1, color="#2b5c8f", label="Behavioral Feature"),
    ]
    plt.legend(handles=legend_elements, loc="lower right", fontsize=10)
    plt.grid(axis="x", linestyle=":", alpha=0.6)
    plt.tight_layout()
    plt.savefig(eval_plot_dir / "feature_importance.png", dpi=150)
    plt.close()

    print(f"  Saved evaluation charts to: {eval_plot_dir.name}/")

    # -------------------------------------------------------------
    # FORMATTED COMPARISON SUMMARY OUTPUT
    # -------------------------------------------------------------
    print("\n" + "=" * 60)
    print("MODEL PERFORMANCE COMPARISON (TEST SET)")
    print("=" * 60)
    print(f"{'Metric':<25} | {'Baseline (No Graph)':<20} | {'FraudGraph (With Graph)':<20}")
    print("-" * 72)
    print(f"{'ROC-AUC':<25} | {base_auc:<20.4f} | {graph_auc:<20.4f}")
    print(f"{'Precision (Default 0.50)':<25} | {base_m50['precision']*100:<19.2f}% | {graph_m50['precision']*100:<19.2f}%")
    print(f"{'Recall (Default 0.50)':<25} | {base_m50['recall']*100:<19.2f}% | {graph_m50['recall']*100:<19.2f}%")
    print(f"{'F1 Score (Default 0.50)':<25} | {base_m50['f1']:<20.4f} | {graph_m50['f1']:<20.4f}")
    print(f"{'False Positive Rate':<25} | {base_m50['false_positive_rate']*100:<19.2f}% | {graph_m50['false_positive_rate']*100:<19.2f}%")
    print("-" * 72)
    print(f"{'Optimal F1 Threshold':<25} | {best_base_thresh['threshold']:<20.2f} | {best_graph_thresh['threshold']:<20.2f}")
    print(f"{'Optimal Precision':<25} | {best_base_thresh['precision']*100:<19.2f}% | {best_graph_thresh['precision']*100:<19.2f}%")
    print(f"{'Optimal Recall':<25} | {best_base_thresh['recall']*100:<19.2f}% | {best_graph_thresh['recall']*100:<19.2f}%")
    print(f"{'Optimal F1 Score':<25} | {best_base_thresh['f1']:<20.4f} | {best_graph_thresh['f1']:<20.4f}")
    print("=" * 60 + "\n")

    return metrics_data


if __name__ == "__main__":
    evaluate_models()
