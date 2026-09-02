"""Unsupervised anomaly detection module using IsolationForest.

Detects multi-dimensional behavioral anomalies and outliers without utilizing
ground-truth fraud labels during training.
"""

from typing import Dict, List, Optional, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib


class AnomalyDetector:
    """Unsupervised behavioral anomaly detector with normalized risk output."""

    def __init__(
        self,
        n_estimators: int = 100,
        contamination: float = 0.03,
        random_state: int = 42,
    ):
        self.model = IsolationForest(
            n_estimators=n_estimators,
            contamination=contamination,
            random_state=random_state,
            n_jobs=-1,
        )
        self.feature_names: List[str] = []
        self.score_min: float = -0.5
        self.score_max: float = 0.5
        self.is_fitted: bool = False

    def fit(self, X: pd.DataFrame, feature_names: Optional[List[str]] = None) -> "AnomalyDetector":
        """Fits IsolationForest strictly on unlabelled feature matrices."""
        if isinstance(X, pd.DataFrame):
            self.feature_names = feature_names or X.columns.tolist()
            X_mat = X.values
        else:
            self.feature_names = feature_names or [f"feat_{i}" for i in range(X.shape[1])]
            X_mat = X

        self.model.fit(X_mat)
        
        # Determine baseline score calibration bounds
        raw_scores = self.model.decision_function(X_mat)
        self.score_min = float(np.percentile(raw_scores, 0.5))
        self.score_max = float(np.percentile(raw_scores, 99.5))
        if self.score_max <= self.score_min:
            self.score_max = self.score_min + 1.0

        self.is_fitted = True
        return self

    def predict_anomaly_score(self, X: pd.DataFrame) -> np.ndarray:
        """Calculates normalized anomaly score scaled to 0 - 100 (100 = highly anomalous outlier)."""
        if not self.is_fitted:
            raise RuntimeError("AnomalyDetector must be fitted before predict_anomaly_score().")

        X_mat = X.values if isinstance(X, pd.DataFrame) else X
        raw_scores = self.model.decision_function(X_mat)

        # Invert score: raw decision_function has lower scores for anomalies
        # Normalize into [0, 100]
        normalized = (self.score_max - raw_scores) / (self.score_max - self.score_min)
        scaled_scores = np.clip(normalized * 100.0, 0.0, 100.0)
        return np.round(scaled_scores, 2)

    def predict_binary(self, X: pd.DataFrame, threshold: float = 65.0) -> np.ndarray:
        """Predicts binary outlier status based on normalized anomaly score threshold."""
        scores = self.predict_anomaly_score(X)
        return (scores >= threshold).astype(int)

    def save(self, filepath: str) -> None:
        """Saves anomaly detector instance to disk."""
        joblib.dump(self, filepath)

    @classmethod
    def load(cls, filepath: str) -> "AnomalyDetector":
        """Loads anomaly detector instance from disk."""
        return joblib.load(filepath)
