"""Transaction-level and behavioral baseline fraud classification model.

Uses RandomForestClassifier trained strictly on single-transaction and historical
customer behavioral features (excluding all graph-derived indicators).
"""

from typing import Dict, List, Optional, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib


class BaselineFraudModel:
    """Supervised baseline classifier trained without graph network features."""

    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: int = 12,
        min_samples_split: int = 5,
        min_samples_leaf: int = 2,
        class_weight: str = "balanced_subsample",
        random_state: int = 42,
    ):
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            class_weight=class_weight,
            random_state=random_state,
            n_jobs=-1,
        )
        self.feature_names: List[str] = []
        self.is_fitted: bool = False

    def fit(self, X: pd.DataFrame, y: np.ndarray, feature_names: Optional[List[str]] = None) -> "BaselineFraudModel":
        """Trains the baseline classifier on training features and binary targets."""
        if isinstance(X, pd.DataFrame):
            self.feature_names = feature_names or X.columns.tolist()
            X_mat = X.values
        else:
            self.feature_names = feature_names or [f"feat_{i}" for i in range(X.shape[1])]
            X_mat = X

        self.model.fit(X_mat, y)
        self.is_fitted = True
        return self

    def predict(self, X: pd.DataFrame, threshold: float = 0.5) -> np.ndarray:
        """Predicts binary fraud class using configurable classification threshold."""
        proba = self.predict_proba(X)
        return (proba >= threshold).astype(int)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Predicts probability of fraud (class 1)."""
        if not self.is_fitted:
            raise RuntimeError("BaselineFraudModel must be fitted before predict_proba().")
        X_mat = X.values if isinstance(X, pd.DataFrame) else X
        # Index 1 is fraud class probability
        return self.model.predict_proba(X_mat)[:, 1]

    def get_feature_importance(self) -> pd.DataFrame:
        """Extracts sorted Gini feature importances for explainability."""
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before extracting feature importances.")
        importances = self.model.feature_importances_
        df = pd.DataFrame({
            "feature": self.feature_names,
            "importance": importances,
            "model": "baseline_random_forest",
        })
        return df.sort_values(by="importance", ascending=False).reset_index(drop=True)

    def save(self, filepath: str) -> None:
        """Saves model instance to disk."""
        joblib.dump(self, filepath)

    @classmethod
    def load(cls, filepath: str) -> "BaselineFraudModel":
        """Loads model instance from disk."""
        return joblib.load(filepath)
