"""
ml/features/engineering.py
Feature engineering pipeline for the irrigation ML system.
Groups: Soil, Weather, Crop, Field, Irrigation History, Temporal, Interaction.
All features documented with agricultural domain rationale.
"""
import sys
import math
import logging
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from ml import config as cfg

logger = logging.getLogger(__name__)

# ── Crop type encoding ────────────────────────────────────────────────────────
CROP_TYPE_MAP: Dict[str, int] = {
    "rice": 0, "wheat": 1, "maize": 2, "corn": 2, "cotton": 3,
    "sugarcane": 4, "soybean": 5, "tomato": 6, "potato": 7,
    "groundnut": 8, "sunflower": 9, "unknown": 10, "standard": 10,
}

GROWTH_STAGE_MAP: Dict[str, int] = {
    "initial": 0, "vegetative": 1, "flowering": 2, "mid season": 3,
    "grain filling": 4, "late season": 5, "ripening": 6, "harvest": 7,
}

SOIL_TYPE_MAP: Dict[str, int] = {
    "sandy": 0, "sandy loam": 1, "loam": 2, "silt loam": 3,
    "clay loam": 4, "silty clay": 5, "clay": 6,
}

SEASON_MAP: Dict[int, int] = {
    12: 0, 1: 0, 2: 0,   # Winter
    3: 1, 4: 1, 5: 1,    # Spring
    6: 2, 7: 2, 8: 2,    # Summer
    9: 3, 10: 3, 11: 3,  # Autumn
}


def _encode_categorical(df: pd.DataFrame) -> pd.DataFrame:
    """Encode crop_type, growth_stage, soil_type to integers."""
    df = df.copy()
    crop_lower = df["crop_type"].str.lower().str.strip() if "crop_type" in df.columns else pd.Series(["unknown"] * len(df))
    df["crop_type_encoded"] = crop_lower.apply(
        lambda c: next((v for k, v in CROP_TYPE_MAP.items() if k in c), 10)
    )
    stage_lower = df["growth_stage"].str.lower().str.strip() if "growth_stage" in df.columns else pd.Series(["vegetative"] * len(df))
    df["growth_stage_encoded"] = stage_lower.apply(
        lambda s: next((v for k, v in GROWTH_STAGE_MAP.items() if k in s), 1)
    )
    soil_lower = df["soil_type"].str.lower().str.strip() if "soil_type" in df.columns else pd.Series(["loam"] * len(df))
    df["soil_type_encoded"] = soil_lower.apply(
        lambda s: next((v for k, v in SOIL_TYPE_MAP.items() if k in s), 2)
    )
    df["stage_water_requirement_mm"] = stage_lower.apply(
        lambda s: next((v for k, v in cfg.STAGE_WATER_REQUIREMENT.items() if k in s),
                       cfg.STAGE_WATER_REQUIREMENT["default"])
    )
    return df


def _soil_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Soil moisture temporal features.
    Rolling stats require sorted timestamp — enforced here.
    """
    df = df.copy()
    if "timestamp" in df.columns:
        df = df.sort_values("timestamp").reset_index(drop=True)

    # Lag
    df["prev_soil_moisture"] = df["soil_moisture"].shift(1).fillna(df["soil_moisture"])

    # Rolling windows (hours as periods since data is 1h interval)
    for w in cfg.ROLLING_WINDOWS_HOURS:
        df[f"rolling_mean_{w}h"] = (
            df["soil_moisture"].rolling(window=w, min_periods=1).mean()
        )
    df["rolling_min_12h"] = df["soil_moisture"].rolling(12, min_periods=1).min()
    df["rolling_max_12h"] = df["soil_moisture"].rolling(12, min_periods=1).max()

    # Trend (linear slope over 6h window)
    df["moisture_trend"] = df["soil_moisture"].rolling(6, min_periods=2).apply(
        lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x) > 1 else 0.0,
        raw=True
    )
    # Change rate (per hour)
    df["moisture_change_rate"] = df["soil_moisture"].diff(1).fillna(0.0)

    # Moisture deficit vs field capacity
    fc = df.get("soil_type", pd.Series(["loam"] * len(df))).apply(
        lambda s: next((v for k, v in cfg.FIELD_CAPACITY.items() if k in s.lower()), cfg.FIELD_CAPACITY["default"])
    )
    df["moisture_deficit"] = (fc - df["soil_moisture"]).clip(lower=0.0)

    return df


def _weather_features(df: pd.DataFrame) -> pd.DataFrame:
    """Weather and forecast features."""
    df = df.copy()
    # Forward-fill forecast columns if missing
    if "forecast_temp_6h" not in df.columns:
        df["forecast_temp_6h"] = df["temperature"]
    if "forecast_rain_prob_6h" not in df.columns:
        df["forecast_rain_prob_6h"] = df["rain_probability"]
    df["forecast_temp_6h"] = df["forecast_temp_6h"].fillna(df["temperature"])
    df["forecast_rain_prob_6h"] = df["forecast_rain_prob_6h"].fillna(df["rain_probability"])
    return df


def _temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """Time-based features from timestamp."""
    df = df.copy()
    if "timestamp" in df.columns:
        ts = pd.to_datetime(df["timestamp"], utc=True)
        df["hour_of_day"] = ts.dt.hour
        df["day_of_week"] = ts.dt.dayofweek
        df["day_of_year"] = ts.dt.dayofyear
        df["season"] = ts.dt.month.map(SEASON_MAP).fillna(2)
    else:
        for col in ["hour_of_day", "day_of_week", "day_of_year", "season"]:
            if col not in df.columns:
                df[col] = 0
    if "days_since_planted" not in df.columns:
        df["days_since_planted"] = 0
    return df


def _interaction_features(df: pd.DataFrame) -> pd.DataFrame:
    """Domain-justified interaction features."""
    df = df.copy()
    # High temperature amplifies water loss from wet soil
    df["sm_x_temp"] = df["soil_moisture"] * df["temperature"]
    # Humidity moderates evapotranspiration
    df["sm_x_humidity"] = df["soil_moisture"] * df["humidity"]
    # If rain is likely AND soil is already moist, irrigation is less needed
    df["rain_prob_x_sm"] = df["rain_probability"] * df["soil_moisture"]
    # Crop water demand × soil moisture deficit
    df["kc_x_sm"] = df["kc_factor"] * (1.0 - df["soil_moisture"] / 100.0)
    return df


def _fill_missing_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure all required columns exist with sensible defaults."""
    defaults = {
        "timestamp": pd.Timestamp.now(tz="UTC"),
        "prev_irrigation_volume": 0.0,
        "hours_since_last_irrigation": 999.0,
        "rolling_7d_irrigation_liters": 0.0,
        "prev_irrigation_duration": 30.0,
        "solar_radiation": 600.0,
        "rainfall_24h": 0.0,
        "temperature_soil": df.get("temperature", pd.Series([25.0] * len(df))),
    }
    for col, default in defaults.items():
        if col not in df.columns:
            df[col] = default
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Full feature engineering pipeline.
    Input:  Raw merged DataFrame from loader.
    Output: Feature-enriched DataFrame ready for model training.
    """
    if df.empty:
        logger.warning("engineer_features received empty DataFrame")
        return df

    df = _fill_missing_columns(df)
    df = _encode_categorical(df)
    df = _soil_features(df)
    df = _weather_features(df)
    df = _temporal_features(df)
    df = _interaction_features(df)

    # Drop any remaining NaN in critical columns
    critical_cols = ["soil_moisture", "temperature", "humidity", "rain_probability"]
    df = df.dropna(subset=[c for c in critical_cols if c in df.columns])

    logger.info(f"Feature engineering complete: {len(df)} rows, {len(df.columns)} columns")
    return df


def get_feature_columns() -> List[str]:
    """Return the canonical ordered list of ML feature columns."""
    from ml.preprocessing.pipeline import ALL_FEATURES
    return ALL_FEATURES
