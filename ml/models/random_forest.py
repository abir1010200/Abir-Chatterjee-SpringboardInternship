"""
ml/models/random_forest.py
Random Forest Classifier and Regressor for smart irrigation scheduling.
Handles:
  1. Binary classification: irrigation_required (0 or 1)
  2. Volume regression: irrigation_volume_liters
  3. Recommended timing: recommended_hour
"""
import sys
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, mean_absolute_error,
    mean_squared_error, r2_score
)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from ml import config as cfg
from ml.preprocessing.pipeline import (
    ALL_FEATURES, TARGET_CLASSIFICATION, TARGET_REGRESSION_VOL, TARGET_REGRESSION_HOUR
)

logger = logging.getLogger(__name__)


class RandomForestIrrigationModel:
    """
    Dual Random Forest architecture:
    - Classifier: Predicts whether irrigation is needed (with class balancing)
    - Regressor: Predicts optimal irrigation volume (in Liters)
    """

    def __init__(
        self,
        n_estimators: int = cfg.RF_N_ESTIMATORS,
        max_depth: int = cfg.RF_MAX_DEPTH,
        min_samples_split: int = cfg.RF_MIN_SAMPLES_SPLIT,
        min_samples_leaf: int = cfg.RF_MIN_SAMPLES_LEAF,
        random_state: int = cfg.RANDOM_SEED,
        class_weight: str = cfg.RF_CLASS_WEIGHT,
    ):
        self.name = "random_forest"
        self.version = "1.0.0"
        self.feature_names: List[str] = ALL_FEATURES

        self.classifier = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            random_state=random_state,
            class_weight=class_weight,
            n_jobs=-1,
        )

        self.regressor = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            random_state=random_state,
            n_jobs=-1,
        )

        self.is_fitted = False

    def fit(
        self,
        X: np.ndarray,
        y_cls: np.ndarray,
        y_vol: Optional[np.ndarray] = None,
        feature_names: Optional[List[str]] = None,
    ) -> "RandomForestIrrigationModel":
        """
        Fit classifier and regressor on feature array.
        y_cls: binary labels (0 or 1)
        y_vol: volume values in Liters
        """
        if feature_names is not None:
            self.feature_names = feature_names

        logger.info(f"Training RF Classifier on {X.shape[0]} samples, {X.shape[1]} features...")
        self.classifier.fit(X, y_cls)

        if y_vol is not None and len(y_vol) > 0:
            logger.info("Training RF Regressor on volume target...")
            self.regressor.fit(X, y_vol)
        else:
            logger.warning("y_vol is None or empty. Skipping regressor fitting.")

        self.is_fitted = True
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Return array of probability [P(0), P(1)] or P(1)."""
        if not self.is_fitted:
            raise RuntimeError("Model is not fitted yet.")
        probs = self.classifier.predict_proba(X)
        return probs[:, 1] if probs.shape[1] > 1 else probs[:, 0]

    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Predict on feature matrix X.
        Returns:
            (irrigation_required, predicted_volume_liters, confidence_scores)
        """
        if not self.is_fitted:
            raise RuntimeError("Model is not fitted yet.")

        probs = self.predict_proba(X)
        pred_cls = (probs >= 0.5).astype(int)

        pred_vol = self.regressor.predict(X)
        # Post-process volume: positive floor and max cap
        pred_vol = np.clip(pred_vol, 0.0, None)
        # If model classifies as no irrigation required, set volume to 0.0
        pred_vol = np.where(pred_cls == 1, np.maximum(cfg.MIN_IRRIGATION_VOLUME_LITERS, pred_vol), 0.0)

        # Confidence is probability distance from decision boundary normalized to [0.5, 1.0]
        confidence = np.maximum(probs, 1.0 - probs)

        return pred_cls, np.round(pred_vol, 1), np.round(confidence, 3)

    def get_feature_importances(self) -> Dict[str, float]:
        """Return dict of {feature_name: importance_score} sorted descending."""
        if not self.is_fitted:
            return {}
        importances = self.classifier.feature_importances_
        names = self.feature_names if len(self.feature_names) == len(importances) else [f"f_{i}" for i in range(len(importances))]
        res = dict(sorted(zip(names, importances), key=lambda x: x[1], reverse=True))
        return {k: round(float(v), 5) for k, v in res.items()}

    def evaluate(
        self,
        X_test: np.ndarray,
        y_cls_test: np.ndarray,
        y_vol_test: Optional[np.ndarray] = None,
    ) -> Dict[str, Any]:
        """Compute comprehensive evaluation metrics for classification and regression."""
        pred_cls, pred_vol, confidence = self.predict(X_test)
        probs = self.predict_proba(X_test)

        metrics: Dict[str, Any] = {
            "model": self.name,
            "accuracy": round(accuracy_score(y_cls_test, pred_cls), 4),
            "precision": round(precision_score(y_cls_test, pred_cls, zero_division=0), 4),
            "recall": round(recall_score(y_cls_test, pred_cls, zero_division=0), 4),
            "f1": round(f1_score(y_cls_test, pred_cls, zero_division=0), 4),
        }

        try:
            metrics["roc_auc"] = round(roc_auc_score(y_cls_test, probs), 4)
        except Exception:
            metrics["roc_auc"] = None

        if y_vol_test is not None:
            mask = y_cls_test == 1
            if np.sum(mask) > 0:
                v_true = y_vol_test[mask]
                v_pred = pred_vol[mask]
                metrics["volume_mae"] = round(mean_absolute_error(v_true, v_pred), 2)
                metrics["volume_rmse"] = round(float(np.sqrt(mean_squared_error(v_true, v_pred))), 2)
                metrics["volume_r2"] = round(r2_score(v_true, v_pred), 4)

        logger.info(f"Random Forest evaluation: {metrics}")
        return metrics

    def save(self, output_dir: Path) -> Path:
        """Save fitted model weights and artifacts using joblib."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        model_path = output_dir / f"{self.name}_v{self.version}.joblib"
        data = {
            "classifier": self.classifier,
            "regressor": self.regressor,
            "feature_names": self.feature_names,
            "version": self.version,
            "name": self.name,
        }
        joblib.dump(data, model_path)
        logger.info(f"Model saved to {model_path}")
        return model_path

    @classmethod
    def load(cls, model_path: Path) -> "RandomForestIrrigationModel":
        """Load fitted model from joblib file."""
        data = joblib.load(model_path)
        instance = cls()
        instance.classifier = data["classifier"]
        instance.regressor = data["regressor"]
        instance.feature_names = data.get("feature_names", ALL_FEATURES)
        instance.version = data.get("version", "1.0.0")
        instance.name = data.get("name", "random_forest")
        instance.is_fitted = True
        return instance
