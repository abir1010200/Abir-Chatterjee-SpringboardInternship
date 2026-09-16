"""
ml/notebooks_or_scripts/02_feature_engineering.py
Week 3: Feature Engineering, Chronological Splitting, and Processed Dataset Persistence.

Performs:
1. Feature extraction & transformation using ml/src/features.py.
2. Time-series chronological train/validation/test split (70/15/15).
3. Dataset persistence under ml/data/processed/ (Parquet + CSV).
4. Data dictionary documentation generation (ml/data/processed/data_dictionary.md).
"""
import sys
import logging
from pathlib import Path
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from ml import config as cfg
from ml.data.loader import load_all_fields_dataset
from ml.data.splitter import chronological_split, get_split_summary
from ml.src.features import extract_features, get_feature_columns
from ml.preprocessing.pipeline import TARGET_CLASSIFICATION, TARGET_REGRESSION_VOL, TARGET_REGRESSION_HOUR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("ml.feature_engineering")

PROCESSED_DIR = cfg.ML_ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def generate_data_dictionary(df: pd.DataFrame, feature_cols: list) -> str:
    """Generate comprehensive Data Dictionary in Markdown format."""
    lines = [
        "# Smart Irrigation System - Data Dictionary & Dataset Schema",
        "",
        "## Overview",
        "This dataset contains agricultural sensor telemetry, weather observations, crop growth metadata, historical irrigation records, and engineered domain features for machine learning irrigation scheduling.",
        "",
        "## Target Variables",
        f"- **`{TARGET_CLASSIFICATION}`** (Binary Class: 0 or 1): Indicates whether field irrigation is required based on soil moisture deficit and weather postponement rules.",
        f"- **`{TARGET_REGRESSION_VOL}`** (Float, Liters): Recommended water volume delivery in Liters.",
        f"- **`{TARGET_REGRESSION_HOUR}`** (Integer, Hour [0-23]): Recommended optimal dispatch hour to minimize evapotranspiration losses.",
        "",
        "## Feature Specifications",
        "| Feature Name | Data Type | Agricultural Rationale & Description |",
        "|---|---|---|",
    ]

    descriptions = {
        "soil_moisture": "Current capacitive soil moisture level (volumetric %). Range: [0, 100]%.",
        "prev_soil_moisture": "Lagged soil moisture level from previous 1-hour interval.",
        "rolling_mean_3h": "3-hour rolling average soil moisture (short-term trend).",
        "rolling_mean_6h": "6-hour rolling average soil moisture (medium-term trend).",
        "rolling_mean_12h": "12-hour rolling average soil moisture (daily trend).",
        "rolling_min_12h": "12-hour rolling minimum soil moisture level.",
        "rolling_max_12h": "12-hour rolling maximum soil moisture level.",
        "moisture_trend": "6-hour linear slope of soil moisture change (rate of drying).",
        "moisture_change_rate": "1-hour instant change in soil moisture level.",
        "moisture_deficit": "Soil moisture deficit below soil Field Capacity (FC - SM).",
        "temperature": "Ambient air temperature (°C).",
        "humidity": "Relative atmospheric humidity (%).",
        "rainfall_1h": "Precipitation in last 1 hour (mm).",
        "rainfall_24h": "Precipitation in last 24 hours (mm).",
        "rain_probability": "Forecasted precipitation probability (%).",
        "solar_radiation": "Solar irradiance (W/m²). Drives soil evaporation.",
        "et0_proxy": "Hargreaves Evapotranspiration proxy (mm/day atmospheric water demand).",
        "forecast_temp_6h": "6-hour ahead temperature forecast (°C).",
        "forecast_rain_prob_6h": "6-hour ahead rain probability forecast (%).",
        "kc_factor": "Crop coefficient factor (Kc) reflecting crop water consumption multiplier.",
        "stage_water_requirement_mm": "Daily water requirement for current crop growth stage (mm/day).",
        "size_hectares": "Total field area in hectares.",
        "prev_irrigation_volume": "Water volume delivered in most recent irrigation event (Liters).",
        "hours_since_last_irrigation": "Time elapsed since last completed irrigation event (hours).",
        "rolling_7d_irrigation_liters": "Cumulative water volume applied over the past 7 days (Liters).",
        "hour_of_day": "Hour of day (0-23). Captures diurnal evapotranspiration cycle.",
        "day_of_week": "Day of week (0-6).",
        "day_of_year": "Day of year (1-365). Captures annual seasonal variations.",
        "season": "Seasonal code (0=Winter, 1=Spring, 2=Summer, 3=Autumn).",
        "days_since_planted": "Number of days elapsed since crop planting date.",
        "crop_type_encoded": "Ordinal encoded crop category integer.",
        "growth_stage_encoded": "Ordinal encoded crop growth stage integer.",
        "soil_type_encoded": "Ordinal encoded soil texture type integer.",
        "sm_x_temp": "Interaction term: Soil moisture x Temperature.",
        "sm_x_humidity": "Interaction term: Soil moisture x Humidity.",
        "rain_prob_x_sm": "Interaction term: Rain probability x Soil moisture.",
        "kc_x_sm": "Interaction term: Crop Kc x Soil moisture deficit.",
    }

    for col in feature_cols:
        dtype = str(df[col].dtype) if col in df.columns else "float64"
        desc = descriptions.get(col, "Engineered telemetry feature.")
        lines.append(f"| `{col}` | `{dtype}` | {desc} |")

    lines.extend([
        "",
        "## Train / Validation / Test Split Strategy",
        "- **Method**: Chronological (Time-Based) Sequential Split.",
        "- **Train Set**: First 70% of chronological time series.",
        "- **Validation Set**: Next 15% of chronological time series.",
        "- **Test Set**: Final 15% of chronological time series.",
        "- **Rationale**: Operational time-series data exhibits temporal dependence and seasonal autocorrelation. Random shuffling causes data leakage from future observations into training history. Chronological split simulates realistic deployment conditions."
    ])

    return "\n".join(lines)


def run_feature_engineering_pipeline():
    """Run full feature engineering, split, and save pipeline."""
    logger.info("=== Running Week 3 Feature Engineering Pipeline ===")
    df_raw = load_all_fields_dataset(min_rows=cfg.SYNTHETIC_MIN_ROWS)
    logger.info(f"Loaded raw dataset with {len(df_raw)} records.")

    # Engineer Features
    df_feat = extract_features(df_raw)
    feature_cols = get_feature_columns()
    logger.info(f"Engineered {len(df_feat.columns)} columns. Recognized {len(feature_cols)} ML features.")

    # Chronological Time-Series Split
    train_df, val_df, test_df = chronological_split(df_feat)
    split_info = get_split_summary(train_df, val_df, test_df)
    logger.info(f"Chronological split complete: {split_info}")

    # Persist Datasets
    full_path = PROCESSED_DIR / "irrigation_dataset_processed.parquet"
    train_path = PROCESSED_DIR / "train_dataset.parquet"
    val_path = PROCESSED_DIR / "val_dataset.parquet"
    test_path = PROCESSED_DIR / "test_dataset.parquet"

    df_feat.to_parquet(full_path, index=False)
    train_df.to_parquet(train_path, index=False)
    val_df.to_parquet(val_path, index=False)
    test_df.to_parquet(test_path, index=False)

    # Export CSV copies as well
    df_feat.to_csv(PROCESSED_DIR / "irrigation_dataset_processed.csv", index=False)
    train_df.to_csv(PROCESSED_DIR / "train_dataset.csv", index=False)

    logger.info(f"Saved processed datasets to {PROCESSED_DIR}")

    # Data Dictionary
    dict_content = generate_data_dictionary(df_feat, feature_cols)
    dict_path = PROCESSED_DIR / "data_dictionary.md"
    with open(dict_path, "w", encoding="utf-8") as f:
        f.write(dict_content)
    logger.info(f"Saved Data Dictionary to {dict_path}")

    return df_feat, train_df, val_df, test_df


if __name__ == "__main__":
    run_feature_engineering_pipeline()
