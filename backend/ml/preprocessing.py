"""Data preprocessing and feature scaling module for FraudGraph ML models.

Ensures strict zero-leakage pipeline:
- Imputers, scalers, and encoders are fitted ONLY on the training split.
- Test and validation splits are transformed using fitted parameters.
"""

from typing import List, Dict, Optional, Tuple, Any
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, RobustScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
import joblib


class DataPreprocessor:
    """Preprocesses numerical and categorical features with zero target leakage."""

    def __init__(
        self,
        numerical_features: Optional[List[str]] = None,
        categorical_features: Optional[List[str]] = None,
        use_robust_scaling: bool = True,
    ):
        self.numerical_features = numerical_features or []
        self.categorical_features = categorical_features or []
        self.use_robust_scaling = use_robust_scaling

        self.num_imputer = SimpleImputer(strategy="median")
        self.cat_imputer = SimpleImputer(strategy="most_frequent")
        self.scaler = RobustScaler() if use_robust_scaling else StandardScaler()
        self.encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)

        self.fitted_feature_names: List[str] = []
        self.is_fitted: bool = False

    def fit(self, X: pd.DataFrame) -> "DataPreprocessor":
        """Fits imputers, scalers, and encoders on the training feature DataFrame."""
        if not isinstance(X, pd.DataFrame):
            raise TypeError("Input X must be a pandas DataFrame.")

        # Determine feature subsets if not provided
        if not self.numerical_features and not self.categorical_features:
            self.numerical_features = X.select_dtypes(include=[np.number]).columns.tolist()
            self.categorical_features = X.select_dtypes(exclude=[np.number]).columns.tolist()

        # Fit numerical transformers
        if self.numerical_features:
            X_num = X[self.numerical_features]
            X_num_imp = self.num_imputer.fit_transform(X_num)
            self.scaler.fit(X_num_imp)

        # Fit categorical transformers
        if self.categorical_features:
            X_cat = X[self.categorical_features].astype(str)
            X_cat_imp = self.cat_imputer.fit_transform(X_cat)
            self.encoder.fit(X_cat_imp)

        # Record transformed column names
        feature_names = []
        if self.numerical_features:
            feature_names.extend(self.numerical_features)
        if self.categorical_features:
            cat_names = self.encoder.get_feature_names_out(self.categorical_features).tolist()
            feature_names.extend(cat_names)

        self.fitted_feature_names = feature_names
        self.is_fitted = True
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Transforms feature DataFrame using fitted parameters."""
        if not self.is_fitted:
            raise RuntimeError("DataPreprocessor must be fitted before calling transform().")

        transformed_blocks = []

        # Transform numerical features
        if self.numerical_features:
            X_num = X[self.numerical_features]
            X_num_imp = self.num_imputer.transform(X_num)
            X_num_scaled = self.scaler.transform(X_num_imp)
            transformed_blocks.append(X_num_scaled)

        # Transform categorical features
        if self.categorical_features:
            X_cat = X[self.categorical_features].astype(str)
            X_cat_imp = self.cat_imputer.transform(X_cat)
            X_cat_encoded = self.encoder.transform(X_cat_imp)
            transformed_blocks.append(X_cat_encoded)

        if not transformed_blocks:
            return pd.DataFrame(index=X.index)

        X_transformed = np.hstack(transformed_blocks)
        return pd.DataFrame(
            X_transformed,
            columns=self.fitted_feature_names,
            index=X.index,
        )

    def fit_transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Fits on training data and returns transformed DataFrame."""
        return self.fit(X).transform(X)

    def save(self, filepath: str) -> None:
        """Serializes preprocessor object to disk using joblib."""
        joblib.dump(self, filepath)

    @classmethod
    def load(cls, filepath: str) -> "DataPreprocessor":
        """Loads serialized preprocessor object from disk."""
        return joblib.load(filepath)
