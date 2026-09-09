"""
ml/models/baseline.py
Rule-based baseline model for irrigation scheduling.
Used as a performance lower bound for ML model comparison.
No machine learning — pure domain rules.
"""
import sys
import logging
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from ml import config as cfg

logger = logging.getLogger(__name__)


class BaselineIrrigationModel:
    """
    Simple rule-based baseline:
    - Irrigate if soil_moisture < threshold AND rain_probability < cutoff
    - Volume: size_ha * kc * 30 mm/event * 10000 L/ha
    - Timing: always morning (06:00)
    """

    def __init__(
        self,
        moisture_threshold: float = None,
        rain_prob_cutoff: float = cfg.RAIN_POSTPONE_THRESHOLD,
        preferred_hour: int = cfg.PREFERRED_IRRIGATION_HOUR_MORNING,
    ):
        self.moisture_threshold = moisture_threshold  # None = use soil-type FC
        self.rain_prob_cutoff = rain_prob_cutoff
        self.preferred_hour = preferred_hour
        self.name = "baseline_rule_based"
        self.version = "1.0.0"

    def _get_threshold(self, row: pd.Series) -> float:
        if self.moisture_threshold is not None:
            return self.moisture_threshold
        soil = str(row.get("soil_type", "loam")).lower()
        fc = next((v for k, v in cfg.FIELD_CAPACITY.items() if k in soil),
                  cfg.FIELD_CAPACITY["default"])
        return fc * cfg.IRRIGATION_TRIGGER_FRACTION

    def predict_row(self, row: pd.Series) -> Tuple[int, float, float, int]:
        """Return (irrigation_required, volume_liters, confidence, recommended_hour)."""
        sm = float(row.get("soil_moisture", 30.0))
        rp = float(row.get("rain_probability", 10.0))
        threshold = self._get_threshold(row)

        required = int(sm < threshold and rp < self.rain_prob_cutoff)

        size_ha = float(row.get("size_hectares", 1.0))
        kc = float(row.get("kc_factor", 1.0))
        volume = (size_ha * kc * 30.0 * 10000) if required else 0.0
        volume = max(cfg.MIN_IRRIGATION_VOLUME_LITERS, min(volume, size_ha * cfg.MAX_LITERS_PER_HECTARE))

        # Confidence: how far soil moisture is from threshold (0.5–1.0)
        deficit_frac = max(0.0, (threshold - sm) / max(threshold, 1.0))
        confidence = min(1.0, 0.5 + deficit_frac * 0.5)

        temp = float(row.get("temperature", 25.0))
        rec_hour = (cfg.PREFERRED_IRRIGATION_HOUR_EVENING if temp > cfg.HIGH_TEMP_EVENING_THRESHOLD
                    else cfg.PREFERRED_IRRIGATION_HOUR_MORNING)

        return required, round(volume, 1), round(confidence, 3), rec_hour

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """Batch predict on a DataFrame. Returns df with prediction columns."""
        results = df.apply(self.predict_row, axis=1, result_type="expand")
        results.columns = ["pred_irrigation_required", "pred_volume_liters",
                           "pred_confidence", "pred_recommended_hour"]
        return pd.concat([df.reset_index(drop=True), results.reset_index(drop=True)], axis=1)

    def evaluate(self, df: pd.DataFrame, target_col: str = "irrigation_required") -> dict:
        """Evaluate against ground-truth labels."""
        from sklearn.metrics import (
            accuracy_score, precision_score, recall_score,
            f1_score, roc_auc_score, mean_absolute_error,
            mean_squared_error, r2_score
        )
        pred_df = self.predict(df)
        y_true = pred_df[target_col].values
        y_pred = pred_df["pred_irrigation_required"].values
        y_conf = pred_df["pred_confidence"].values

        metrics = {
            "model": self.name,
            "accuracy": round(accuracy_score(y_true, y_pred), 4),
            "precision": round(precision_score(y_true, y_pred, zero_division=0), 4),
            "recall": round(recall_score(y_true, y_pred, zero_division=0), 4),
            "f1": round(f1_score(y_true, y_pred, zero_division=0), 4),
        }
        try:
            metrics["roc_auc"] = round(roc_auc_score(y_true, y_conf), 4)
        except Exception:
            metrics["roc_auc"] = None

        # Volume regression (only when irrigation is required)
        mask = y_true == 1
        if mask.sum() > 0:
            vol_true = df["irrigation_volume_liters"].values[mask]
            vol_pred = pred_df["pred_volume_liters"].values[mask]
            metrics["volume_mae"] = round(mean_absolute_error(vol_true, vol_pred), 2)
            metrics["volume_rmse"] = round(mean_squared_error(vol_true, vol_pred) ** 0.5, 2)

        logger.info(f"Baseline evaluation: {metrics}")
        return metrics
