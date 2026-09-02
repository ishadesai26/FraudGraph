"""End-to-end training pipeline for FraudGraph machine learning models.

Executes:
1. Data and Graph Feature Loading
2. Feature Matrix Construction
3. Time-Aware Train/Validation/Test Splitting
4. Preprocessing Fit (Strict Zero-Leakage)
5. Baseline Model Training (Behavioral only)
6. Unsupervised Anomaly Detector Training (IsolationForest)
7. FraudGraph Model Training (Behavioral + Graph)
8. Artifact Serialization under backend/ml/artifacts/
"""

import sys
import json
from pathlib import Path
import pandas as pd
import numpy as np

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


def train_models() -> dict:
    """Executes the complete machine learning training pipeline."""
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    settings = get_settings()
    artifacts_dir = Path(__file__).resolve().parent / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    processed_dir = settings.processed_data_dir
    processed_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("FRAUDGRAPH PHASE 3: ML RISK ENGINE TRAINING PIPELINE")
    print("=" * 60)

    # -------------------------------------------------------------
    # 1. LOAD DATASETS & GRAPH FEATURES
    # -------------------------------------------------------------
    print("\n[1/6] Loading Phase 1 Datasets & Phase 2 Graph Features...")
    builder = GraphBuilder(data_dir=settings.raw_data_dir)
    datasets = builder.load_datasets()

    # Build or retrieve graph features
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

    print(f"  Loaded {len(datasets['transactions']):,} transactions across {len(datasets['customers']):,} customers.")
    print(f"  Extracted {graph_features_df.shape[1]} graph features.")

    # -------------------------------------------------------------
    # 2. FEATURE ENGINEERING & TIME-AWARE SPLITTING
    # -------------------------------------------------------------
    print("\n[2/6] Building Features & Performing Time-Aware Split (70/15/15)...")
    feat_engineer = MLFeatureEngineer(
        datasets=datasets,
        graph_features_df=graph_features_df,
        rings_df=rings_df,
        members_df=members_df,
    )
    splits = feat_engineer.get_feature_splits(train_ratio=0.70, val_ratio=0.15, test_ratio=0.15)

    y_train = splits["y_train"]
    y_val = splits["y_val"]
    y_test = splits["y_test"]

    print(f"  Training Split:   {len(y_train):,} samples (Fraud: {y_train.sum()} | {y_train.mean()*100:.2f}%)")
    print(f"  Validation Split: {len(y_val):,} samples (Fraud: {y_val.sum()} | {y_val.mean()*100:.2f}%)")
    print(f"  Test Split:       {len(y_test):,} samples (Fraud: {y_test.sum()} | {y_test.mean()*100:.2f}%)")

    # -------------------------------------------------------------
    # 3. PREPROCESSING PIPELINE (Fitted ONLY on Training Set)
    # -------------------------------------------------------------
    print("\n[3/6] Fitting Preprocessors on Training Data...")
    # Baseline Preprocessor
    prep_baseline = DataPreprocessor(
        numerical_features=splits["baseline_numerical"],
        categorical_features=splits["baseline_categorical"],
        use_robust_scaling=True,
    )
    X_base_train_prep = prep_baseline.fit_transform(splits["X_baseline_train"])
    X_base_val_prep = prep_baseline.transform(splits["X_baseline_val"])
    X_base_test_prep = prep_baseline.transform(splits["X_baseline_test"])

    # Graph Preprocessor
    prep_graph = DataPreprocessor(
        numerical_features=splits["graph_numerical"],
        categorical_features=splits["graph_categorical"],
        use_robust_scaling=True,
    )
    X_graph_train_prep = prep_graph.fit_transform(splits["X_graph_train"])
    X_graph_val_prep = prep_graph.transform(splits["X_graph_val"])
    X_graph_test_prep = prep_graph.transform(splits["X_graph_test"])

    # Save preprocessors
    prep_baseline.save(str(artifacts_dir / "preprocessor_baseline.joblib"))
    prep_graph.save(str(artifacts_dir / "preprocessor_graph.joblib"))
    print("  Saved preprocessor artifacts to backend/ml/artifacts/")

    # -------------------------------------------------------------
    # 4. TRAIN BASELINE SUPERVISED MODEL
    # -------------------------------------------------------------
    print("\n[4/6] Training Baseline RandomForest (Behavioral Features Only)...")
    baseline_model = BaselineFraudModel(
        n_estimators=100,
        max_depth=12,
        class_weight="balanced_subsample",
        random_state=42,
    )
    baseline_model.fit(X_base_train_prep, y_train)
    baseline_model.save(str(artifacts_dir / "baseline_model.joblib"))

    # Validation check
    val_base_preds = baseline_model.predict(X_base_val_prep, threshold=0.5)
    val_base_f1 = float(np.sum((val_base_preds == 1) & (y_val == 1)))
    print(f"  Baseline Model trained. (Val True Positives: {int(val_base_f1)}/{y_val.sum()})")

    # -------------------------------------------------------------
    # 5. TRAIN UNSUPERVISED ANOMALY DETECTOR
    # -------------------------------------------------------------
    print("\n[5/6] Training Unsupervised Anomaly Detector (IsolationForest)...")
    anomaly_detector = AnomalyDetector(
        n_estimators=100,
        contamination=0.03,
        random_state=42,
    )
    anomaly_detector.fit(X_base_train_prep)
    anomaly_detector.save(str(artifacts_dir / "anomaly_model.joblib"))
    print("  Anomaly Detector trained on unlabelled features.")

    # -------------------------------------------------------------
    # 6. TRAIN FRAUDGRAPH GRAPH-ENHANCED MODEL
    # -------------------------------------------------------------
    print("\n[6/6] Training FraudGraph Model (Behavioral + Graph Relational Features)...")
    fraudgraph_model = FraudGraphModel(
        n_estimators=120,
        max_depth=14,
        class_weight="balanced_subsample",
        random_state=42,
    )
    fraudgraph_model.fit(X_graph_train_prep, y_train)
    fraudgraph_model.save(str(artifacts_dir / "fraudgraph_model.joblib"))

    # Extract and save feature importances
    base_imp_df = baseline_model.get_feature_importance()
    graph_imp_df = fraudgraph_model.get_feature_importance()

    combined_importances = {
        "baseline_features": base_imp_df.to_dict(orient="records"),
        "fraudgraph_features": graph_imp_df.to_dict(orient="records"),
    }
    feat_imp_path = processed_dir / "feature_importance.json"
    with open(feat_imp_path, "w", encoding="utf-8") as f:
        json.dump(combined_importances, f, indent=2)
    print(f"  Saved feature importance breakdown to {feat_imp_path.name}")

    print("\n" + "=" * 60)
    print("TRAINING SUMMARY")
    print("=" * 60)
    print(f"Baseline Model Features:    {len(prep_baseline.fitted_feature_names)}")
    print(f"FraudGraph Model Features:  {len(prep_graph.fitted_feature_names)}")
    print("Artifacts generated under:  backend/ml/artifacts/")
    print("  - preprocessor_baseline.joblib")
    print("  - preprocessor_graph.joblib")
    print("  - baseline_model.joblib")
    print("  - anomaly_model.joblib")
    print("  - fraudgraph_model.joblib")
    print("=" * 60 + "\n")

    return {
        "train_samples": len(y_train),
        "val_samples": len(y_val),
        "test_samples": len(y_test),
        "baseline_features_count": len(prep_baseline.fitted_feature_names),
        "graph_features_count": len(prep_graph.fitted_feature_names),
        "artifacts_dir": str(artifacts_dir),
    }


if __name__ == "__main__":
    train_models()
