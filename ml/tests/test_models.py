"""
ml/tests/test_models.py
Unit and validation tests for Baseline, Random Forest, Gradient Boosting, and LSTM models.
"""
import sys
import tempfile
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from ml.data.synthetic_generator import generate_synthetic_dataset
from ml.features.engineering import engineer_features
from ml.preprocessing.pipeline import build_preprocessing_pipeline, ALL_FEATURES
from ml.models.baseline import BaselineIrrigationModel
from ml.models.random_forest import RandomForestIrrigationModel
from ml.models.gradient_boosting import GradientBoostingIrrigationModel
from ml.models.lstm import LSTMIrrigationModel


@pytest.fixture(scope="module")
def prepared_dataset():
    raw = generate_synthetic_dataset(days=15, interval_hours=1)
    df = engineer_features(raw)
    pipe = build_preprocessing_pipeline()
    X = pipe.fit_transform(df)
    y_cls = df["irrigation_required"].values.astype(int)
    y_vol = df["irrigation_volume_liters"].values.astype(float)
    return df, X, y_cls, y_vol


def test_baseline_model(prepared_dataset):
    df, _, _, _ = prepared_dataset
    model = BaselineIrrigationModel()
    results = model.evaluate(df)
    assert "accuracy" in results
    assert "f1" in results
    assert results["accuracy"] >= 0.0


def test_random_forest_model(prepared_dataset):
    _, X, y_cls, y_vol = prepared_dataset
    model = RandomForestIrrigationModel(n_estimators=10, max_depth=5)
    model.fit(X, y_cls, y_vol=y_vol, feature_names=ALL_FEATURES)

    pred_cls, pred_vol, conf = model.predict(X)
    assert len(pred_cls) == len(X)
    assert len(pred_vol) == len(X)
    assert len(conf) == len(X)
    assert np.all((pred_cls == 0) | (pred_cls == 1))
    assert np.all(conf >= 0.5)

    importances = model.get_feature_importances()
    assert len(importances) > 0

    with tempfile.TemporaryDirectory() as tmpdir:
        saved_path = model.save(Path(tmpdir))
        assert saved_path.exists()
        loaded = RandomForestIrrigationModel.load(saved_path)
        p2_cls, p2_vol, _ = loaded.predict(X)
        assert np.array_equal(pred_cls, p2_cls)


def test_gradient_boosting_model(prepared_dataset):
    _, X, y_cls, y_vol = prepared_dataset
    model = GradientBoostingIrrigationModel(n_estimators=10, max_depth=3)
    model.fit(X, y_cls, y_vol=y_vol, feature_names=ALL_FEATURES)

    pred_cls, pred_vol, conf = model.predict(X)
    assert len(pred_cls) == len(X)
    assert np.all((pred_cls == 0) | (pred_cls == 1))

    with tempfile.TemporaryDirectory() as tmpdir:
        saved_path = model.save(Path(tmpdir))
        assert saved_path.exists()
        loaded = GradientBoostingIrrigationModel.load(saved_path)
        p2_cls, _, _ = loaded.predict(X)
        assert np.array_equal(pred_cls, p2_cls)


def test_lstm_model(prepared_dataset):
    df, _, _, _ = prepared_dataset
    model = LSTMIrrigationModel(seq_len=6, hidden_dim=16, num_layers=1, max_epochs=2)
    model.fit(df)

    pred_cls, pred_vol, conf = model.predict(df)
    assert len(pred_cls) > 0
    assert np.all((pred_cls == 0) | (pred_cls == 1))

    with tempfile.TemporaryDirectory() as tmpdir:
        saved_path = model.save(Path(tmpdir))
        assert saved_path.exists()
        loaded = LSTMIrrigationModel.load(saved_path)
        p2_cls, _, _ = loaded.predict(df)
        assert np.array_equal(pred_cls, p2_cls)
