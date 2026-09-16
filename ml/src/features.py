"""
ml/src/features.py
Agricultural domain feature engineering pipeline.
Calculates soil moisture dynamics, weather proxies (ET0), crop growth factors,
irrigation history metrics, and temporal features for irrigation prediction models.
"""
import sys
import math
import logging
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from ml import config as cfg
from ml.features.engineering import (
    CROP_TYPE_MAP, GROWTH_STAGE_MAP, SOIL_TYPE_MAP, SEASON_MAP,
    engineer_features as base_engineer_features
)
from ml.preprocessing.pipeline import ALL_FEATURES, NUMERIC_FEATURES, CATEGORICAL_FEATURES

logger = logging.getLogger(__name__)


def compute_hargreaves_et0(temp: float, humidity: float, solar_rad: float) -> float:
    """
    Simplified Hargreaves Evapotranspiration (ET0) proxy in mm/day.
    Uses temperature, humidity, and solar radiation to estimate atmospheric water demand.
    """
    # Base Hargreaves formula proxy
    temp_term = max(0.0, temp + 17.8)
    rad_term = max(0.0, solar_rad) / 2450.0  # MJ/m2/day proxy
    humidity_modifier = max(0.2, (100.0 - humidity) / 100.0)
    et0 = 0.0023 * temp_term * math.sqrt(abs(temp * 0.2 + 2.0)) * rad_term * 24.0 * humidity_modifier
    return max(0.5, min(12.0, et0))


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract and engineer complete set of features from input telemetry DataFrame.
    Calculates soil rates of change, rolling metrics, ET0 proxy, crop water demands,
    and interaction terms.
    """
    df_out = base_engineer_features(df)
    
    # Add explicit ET0 proxy column if not present
    if "et0_proxy" not in df_out.columns:
        et0_vals = []
        for _, row in df_out.iterrows():
            t = float(row.get("temperature", 25.0))
            h = float(row.get("humidity", 50.0))
            sr = float(row.get("solar_radiation", 600.0))
            et0_vals.append(compute_hargreaves_et0(t, h, sr))
        df_out["et0_proxy"] = et0_vals

    return df_out


def get_feature_columns() -> List[str]:
    """Return the ordered list of canonical ML feature names."""
    return ALL_FEATURES
