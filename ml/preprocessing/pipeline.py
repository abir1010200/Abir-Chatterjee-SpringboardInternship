"""
ml/preprocessing/pipeline.py
Scikit-learn preprocessing pipeline for ML training and inference.
Handles imputation, scaling, and encoding of heterogeneous features.
"""
import sys
import logging
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Optional, Tuple

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, LabelEncoder, OrdinalEncoder
from sklearn.compose import ColumnTransformer

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from ml import config as cfg

logger = logging.getLogger(__name__)

# ── Feature column definitions ────────────────────────────────────────────────
NUMERIC_FEATURES = [
    "soil_moisture", "prev_soil_moisture",
    "rolling_mean_3h", "rolling_mean_6h", "rolling_mean_12h",
    "rolling_min_12h", "rolling_max_12h",
    "moisture_trend", "moisture_change_rate", "moisture_deficit",
    "temperature", "humidity", "rainfall_1h", "rainfall_24h",
    "rain_probability", "solar_radiation",
    "forecast_temp_6h", "forecast_rain_prob_6h",
    "kc_factor", "stage_water_requirement_mm",
    "size_hectares",
    "prev_irrigation_volume", "hours_since_last_irrigation",
    "rolling_7d_irrigation_liters",
    "hour_of_day", "day_of_week", "day_of_year", "season",
    "days_since_planted",
    "sm_x_temp", "sm_x_humidity", "rain_prob_x_sm", "kc_x_sm",
]

CATEGORICAL_FEATURES = [
    "crop_type_encoded", "growth_stage_encoded", "soil_type_encoded",
]

ALL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES

TARGET_CLASSIFICATION = "irrigation_required"
TARGET_REGRESSION_VOL = "irrigation_volume_liters"
TARGET_REGRESSION_HOUR = "recommended_hour"


def build_preprocessing_pipeline() -> ColumnTransformer:
    """Build sklearn ColumnTransformer for numeric + categorical features."""
    numeric_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    # Categorical features are already label-encoded integers; just impute
    cat_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
    ])
    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipe, NUMERIC_FEATURES),
            ("cat", cat_pipe, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )


def get_feature_names() -> List[str]:
    """Return the ordered list of feature column names after transformation."""
    return NUMERIC_FEATURES + CATEGORICAL_FEATURES


def get_available_features(df: pd.DataFrame) -> List[str]:
    """Return only features that exist in the given DataFrame."""
    return [c for c in ALL_FEATURES if c in df.columns]
