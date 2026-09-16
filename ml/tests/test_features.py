"""
ml/tests/test_features.py
Unit tests for agricultural feature engineering pipeline.
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta

from ml.src.features import extract_features, compute_hargreaves_et0, get_feature_columns
from ml.preprocessing.pipeline import ALL_FEATURES, build_preprocessing_pipeline


def test_hargreaves_et0():
    """Test Hargreaves ET0 calculation output within realistic bounds."""
    et0 = compute_hargreaves_et0(temp=30.0, humidity=40.0, solar_rad=800.0)
    assert 0.5 <= et0 <= 12.0


def test_extract_features_columns():
    """Test that feature extraction generates required feature columns."""
    now = datetime.now(timezone.utc)
    sample_data = []
    for i in range(24):
        sample_data.append({
            "timestamp": now + timedelta(hours=i),
            "field_id": 1,
            "soil_moisture": 25.0 - i * 0.2,
            "temperature": 28.0 + (i % 5),
            "humidity": 60.0 - (i % 10),
            "rainfall_1h": 0.0,
            "rainfall_24h": 0.0,
            "rain_probability": 10.0,
            "solar_radiation": 500.0,
            "crop_type": "Wheat",
            "growth_stage": "Vegetative",
            "kc_factor": 1.15,
            "size_hectares": 2.5,
            "soil_type": "Clay Loam",
            "irrigation_required": 0,
            "irrigation_volume_liters": 0.0,
        })
    df = pd.DataFrame(sample_data)
    df_feat = extract_features(df)

    for col in ALL_FEATURES:
        assert col in df_feat.columns, f"Missing feature column: {col}"


def test_preprocessing_pipeline_fit_transform():
    """Test Scikit-Learn ColumnTransformer pipeline fit and transform."""
    now = datetime.now(timezone.utc)
    sample_data = [{
        "timestamp": now,
        "field_id": 1,
        "soil_moisture": 25.0,
        "temperature": 28.0,
        "humidity": 60.0,
        "rainfall_1h": 0.0,
        "rainfall_24h": 0.0,
        "rain_probability": 10.0,
        "solar_radiation": 500.0,
        "crop_type": "Wheat",
        "growth_stage": "Vegetative",
        "kc_factor": 1.15,
        "size_hectares": 2.5,
        "soil_type": "Clay Loam",
    }]
    df = pd.DataFrame(sample_data)
    df_feat = extract_features(df)

    pipe = build_preprocessing_pipeline()
    X_transformed = pipe.fit_transform(df_feat)
    assert X_transformed.shape[0] == 1
    assert X_transformed.shape[1] == len(ALL_FEATURES)
