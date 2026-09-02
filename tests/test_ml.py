"""Unit and integration test suite for FraudGraph Phase 3 Machine Learning Engine."""

import os
import json
import pytest
import numpy as np
import pandas as pd
from pathlib import Path

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
from backend.ml.evaluate import calculate_metrics_at_threshold


@pytest.fixture(scope="module")
def ml_pipeline_data():
    """Builds and caches feature matrices and splits for the test suite."""
    settings = get_settings()
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
    return {
        "datasets": datasets,
        "feat_engineer": feat_engineer,
        "splits": splits,
    }


def test_feature_generation_and_shapes(ml_pipeline_data):
    """Verifies feature matrix generation and non-empty columns."""
    splits = ml_pipeline_data["splits"]
    full_df = splits["full_df"]

    assert len(full_df) == 10000
    assert "amount_log" in full_df.columns
    assert "time_of_day_sin" in full_df.columns
    assert "time_of_day_cos" in full_df.columns
    assert "customer_velocity_per_day" in full_df.columns
    assert "network_risk_score" in full_df.columns
    assert "degree" in full_df.columns


def test_target_leakage_prevention(ml_pipeline_data):
    """Verifies that ground-truth target labels are excluded from feature matrices."""
    splits = ml_pipeline_data["splits"]
    leakage_cols = {"is_fraud", "fraud_ring_id", "fraud_type"}

    for split_key in ["X_baseline_train", "X_baseline_val", "X_baseline_test", "X_graph_train", "X_graph_val", "X_graph_test"]:
        df = splits[split_key]
        for col in leakage_cols:
            assert col not in df.columns, f"Target leakage detected: '{col}' found in '{split_key}'"


def test_time_aware_split_integrity(ml_pipeline_data):
    """Verifies chronological order and disjoint non-overlapping indices."""
    splits = ml_pipeline_data["splits"]

    meta_train = splits["meta_train"]
    meta_val = splits["meta_val"]
    meta_test = splits["meta_test"]

    assert len(meta_train) == 7000
    assert len(meta_val) == 1500
    assert len(meta_test) == 1500

    # Ensure chronological order
    max_train_ts = pd.to_datetime(meta_train["timestamp"]).max()
    min_val_ts = pd.to_datetime(meta_val["timestamp"]).min()
    max_val_ts = pd.to_datetime(meta_val["timestamp"]).max()
    min_test_ts = pd.to_datetime(meta_test["timestamp"]).min()

    assert max_train_ts <= min_val_ts
    assert max_val_ts <= min_test_ts


def test_preprocessor_zero_leakage_and_transforms(ml_pipeline_data):
    """Verifies that DataPreprocessor fits on train data and transforms cleanly."""
    splits = ml_pipeline_data["splits"]

    prep = DataPreprocessor(
        numerical_features=splits["baseline_numerical"],
        categorical_features=splits["baseline_categorical"],
    )

    X_train_prep = prep.fit_transform(splits["X_baseline_train"])
    X_val_prep = prep.transform(splits["X_baseline_val"])
    X_test_prep = prep.transform(splits["X_baseline_test"])

    assert prep.is_fitted
    assert X_train_prep.shape[0] == 7000
    assert X_val_prep.shape[0] == 1500
    assert X_test_prep.shape[0] == 1500
    assert not np.isnan(X_train_prep.values).any()
    assert not np.isnan(X_test_prep.values).any()


def test_baseline_model_training_and_serialization(ml_pipeline_data, tmp_path):
    """Verifies BaselineFraudModel fit, prediction, probability bounds, and joblib serialization."""
    splits = ml_pipeline_data["splits"]
    prep = DataPreprocessor(
        numerical_features=splits["baseline_numerical"],
        categorical_features=splits["baseline_categorical"],
    )
    X_train = prep.fit_transform(splits["X_baseline_train"])
    y_train = splits["y_train"]

    model = BaselineFraudModel(n_estimators=20, max_depth=6, random_state=42)
    model.fit(X_train, y_train)

    assert model.is_fitted
    probs = model.predict_proba(X_train)
    assert len(probs) == len(y_train)
    assert np.all((probs >= 0.0) & (probs <= 1.0))

    # Test serialization
    save_path = tmp_path / "test_baseline.joblib"
    model.save(str(save_path))
    loaded_model = BaselineFraudModel.load(str(save_path))
    loaded_probs = loaded_model.predict_proba(X_train)
    np.testing.assert_allclose(probs, loaded_probs)


def test_anomaly_detector_training_and_scoring(ml_pipeline_data, tmp_path):
    """Verifies IsolationForest anomaly detector bounds (0-100) and unlabelled training."""
    splits = ml_pipeline_data["splits"]
    prep = DataPreprocessor(
        numerical_features=splits["baseline_numerical"],
        categorical_features=splits["baseline_categorical"],
    )
    X_train = prep.fit_transform(splits["X_baseline_train"])

    detector = AnomalyDetector(n_estimators=20, contamination=0.03, random_state=42)
    detector.fit(X_train)

    assert detector.is_fitted
    scores = detector.predict_anomaly_score(X_train)
    assert len(scores) == len(X_train)
    assert np.all((scores >= 0.0) & (scores <= 100.0))

    # Test serialization
    save_path = tmp_path / "test_anomaly.joblib"
    detector.save(str(save_path))
    loaded_detector = AnomalyDetector.load(str(save_path))
    loaded_scores = loaded_detector.predict_anomaly_score(X_train)
    np.testing.assert_allclose(scores, loaded_scores)


def test_graph_model_training_and_feature_importances(ml_pipeline_data):
    """Verifies FraudGraphModel training and feature importance categorization."""
    splits = ml_pipeline_data["splits"]
    prep = DataPreprocessor(
        numerical_features=splits["graph_numerical"],
        categorical_features=splits["graph_categorical"],
    )
    X_train = prep.fit_transform(splits["X_graph_train"])
    y_train = splits["y_train"]

    model = FraudGraphModel(n_estimators=20, max_depth=6, random_state=42)
    model.fit(X_train, y_train)

    assert model.is_fitted
    imp_df = model.get_feature_importance()
    assert "feature" in imp_df.columns
    assert "importance" in imp_df.columns
    assert "category" in imp_df.columns
    assert set(imp_df["category"]).issubset({"graph_relational", "transaction_behavioral"})


def test_composite_risk_scorer_calculations():
    """Verifies CompositeRiskScorer formulas, tier classification, and signal generation."""
    scorer = CompositeRiskScorer(weight_model=0.50, weight_network=0.25, weight_anomaly=0.25)

    # Test Low Risk
    res_low = scorer.score_single_event(model_prob=0.10, network_risk=10.0, anomaly_score=15.0)
    assert res_low["risk_level"] == "LOW"
    assert res_low["risk_score"] < 35.0

    # Test Critical Risk
    res_crit = scorer.score_single_event(model_prob=0.95, network_risk=90.0, anomaly_score=85.0)
    assert res_crit["risk_level"] == "CRITICAL"
    assert res_crit["risk_score"] >= 80.0
    assert len(res_crit["signals"]) >= 3

    # Test Batch
    batch_res = scorer.score_batch(
        model_probs=np.array([0.1, 0.9]),
        network_risks=np.array([5.0, 95.0]),
        anomaly_scores=np.array([10.0, 80.0]),
    )
    assert len(batch_res) == 2
    assert batch_res["risk_level"].iloc[0] == "LOW"
    assert batch_res["risk_level"].iloc[1] in ["HIGH", "CRITICAL"]


def test_multi_threshold_analysis_validity():
    """Verifies mathematical consistency of threshold analysis metrics."""
    y_true = np.array([1, 1, 0, 0, 0, 1, 0, 1])
    y_proba = np.array([0.9, 0.8, 0.2, 0.1, 0.3, 0.7, 0.4, 0.6])

    m = calculate_metrics_at_threshold(y_true, y_proba, threshold=0.5)
    cm = m["confusion_matrix"]

    assert cm["true_negatives"] + cm["false_positives"] + cm["false_negatives"] + cm["true_positives"] == len(y_true)
    assert 0.0 <= m["precision"] <= 1.0
    assert 0.0 <= m["recall"] <= 1.0
    assert 0.0 <= m["f1"] <= 1.0
    assert 0.0 <= m["false_positive_rate"] <= 1.0


def test_ml_artifacts_and_metrics_files_exist():
    """Verifies that model artifacts, metrics JSON, and evaluation charts exist on disk."""
    artifacts_dir = Path(__file__).resolve().parent.parent / "backend" / "ml" / "artifacts"
    processed_dir = Path(__file__).resolve().parent.parent / "data" / "processed"
    eval_dir = processed_dir / "evaluation"

    expected_artifacts = [
        "preprocessor_baseline.joblib",
        "preprocessor_graph.joblib",
        "baseline_model.joblib",
        "anomaly_model.joblib",
        "fraudgraph_model.joblib",
    ]
    for art in expected_artifacts:
        assert (artifacts_dir / art).exists(), f"Artifact missing: {art}"

    assert (processed_dir / "model_metrics.json").exists()
    assert (processed_dir / "feature_importance.json").exists()
    assert (eval_dir / "roc_curves.png").exists()
    assert (eval_dir / "pr_curves.png").exists()
    assert (eval_dir / "confusion_matrices.png").exists()
    assert (eval_dir / "feature_importance.png").exists()
