"""
ml/tests/test_features.py
Unit tests for feature engineering, encoding, and data transformation pipeline.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from ml.data.synthetic_generator import generate_synthetic_dataset
from ml.features.engineering import (
    engineer_features, _soil_features, _encode_categorical, _interaction_features
)
from ml.preprocessing.pipeline import build_preprocessing_pipeline, ALL_FEATURES


@pytest.fixture
def sample_raw_data() -> pd.DataFrame:
    """Generate a quick 100-row synthetic dataset for testing."""
    return generate_synthetic_dataset(days=10, interval_hours=2)


def test_encode_categorical(sample_raw_data: pd.DataFrame):
    df = _encode_categorical(sample_raw_data)
    assert "crop_type_encoded" in df.columns
    assert "growth_stage_encoded" in df.columns
    assert "soil_type_encoded" in df.columns
    assert "stage_water_requirement_mm" in df.columns
    assert df["crop_type_encoded"].dtype in [np.int32, np.int64, int]


def test_soil_features(sample_raw_data: pd.DataFrame):
    df = _soil_features(sample_raw_data)
    assert "prev_soil_moisture" in df.columns
    assert "rolling_mean_3h" in df.columns
    assert "rolling_mean_6h" in df.columns
    assert "moisture_trend" in df.columns
    assert "moisture_change_rate" in df.columns
    assert "moisture_deficit" in df.columns
    # Check no nulls created in rolling mean
    assert df["rolling_mean_3h"].isnull().sum() == 0


def test_interaction_features(sample_raw_data: pd.DataFrame):
    df = _interaction_features(sample_raw_data)
    assert "sm_x_temp" in df.columns
    assert "sm_x_humidity" in df.columns
    assert "rain_prob_x_sm" in df.columns
    assert "kc_x_sm" in df.columns


def test_full_feature_pipeline(sample_raw_data: pd.DataFrame):
    df = engineer_features(sample_raw_data)
    for col in ALL_FEATURES:
        assert col in df.columns, f"Expected feature {col} missing after engineering"
    assert len(df) > 0


def test_preprocessing_pipeline(sample_raw_data: pd.DataFrame):
    df = engineer_features(sample_raw_data)
    pipeline = build_preprocessing_pipeline()
    pipeline.fit(df)
    transformed = pipeline.transform(df)
    assert transformed.shape[0] == len(df)
    assert transformed.shape[1] == len(ALL_FEATURES)
    assert not np.isnan(transformed).any()
