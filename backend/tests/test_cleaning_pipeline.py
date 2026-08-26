import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from backend.main import app
from backend.app.services.cleaning.validator import TelemetryValidator

client = TestClient(app)

def test_telemetry_gap_detection():
    now = datetime.now(timezone.utc)
    # Series with a 90-minute gap between sample 1 and sample 2
    timestamps = [
        now - timedelta(hours=3),
        now - timedelta(hours=2, minutes=45),
        now - timedelta(minutes=45),  # 2h gap
        now - timedelta(minutes=30),
        now - timedelta(minutes=15),
        now
    ]
    gaps = TelemetryValidator.detect_telemetry_gaps(timestamps, expected_interval_minutes=15.0)
    assert len(gaps) >= 1
    assert gaps[0]["gap_duration_minutes"] >= 30

def test_zscore_outlier_detection():
    # 9 normal moisture values around 35%, 1 extreme outlier spike at 99%
    values = [35.1, 35.4, 34.9, 35.2, 35.0, 99.0, 35.3, 34.8, 35.2, 35.1]
    outliers = TelemetryValidator.detect_outliers_zscore(values, threshold=2.5)
    assert len(outliers) == 10
    assert outliers[5] is True  # 99.0 is flagged as outlier
    assert outliers[0] is False

def test_run_cleaning_job_endpoint():
    response = client.post("/api/cleaning/field/1/run")
    assert response.status_code == 200
    data = response.json()
    assert "total_readings" in data
    assert "valid_readings" in data
    assert "status" in data

def test_get_ml_prepared_dataset_endpoint():
    response = client.get("/api/cleaning/field/1/ml-dataset?limit=50")
    assert response.status_code == 200
    data = response.json()
    assert data["field_id"] == 1
    assert "features" in data
    assert "target_variables" in data
    assert "data" in data
    if len(data["data"]) > 0:
        sample = data["data"][0]
        assert "soil_moisture" in sample
        assert "air_temperature" in sample
        assert "kc_factor" in sample
        assert "moisture_deficit" in sample
