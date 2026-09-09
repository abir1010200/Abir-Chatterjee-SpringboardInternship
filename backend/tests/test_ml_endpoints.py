import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_ml_health_endpoint():
    response = client.get("/api/ml/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ml-irrigation-serving"
    assert "active_model" in data


def test_ml_model_info_endpoint():
    response = client.get("/api/ml/model/info")
    assert response.status_code == 200
    data = response.json()
    assert "active_model" in data
    assert "version" in data
    assert "metrics" in data


def test_ml_predict_irrigation_endpoint():
    payload = {
        "field_id": 1,
        "soil_moisture": 22.0,
        "temperature": 32.0,
        "humidity": 40.0,
        "rainfall_1h": 0.0,
        "rainfall_24h": 0.0,
        "rain_probability": 10.0,
        "solar_radiation": 700.0,
        "soil_type": "Clay Loam",
        "crop_type": "Wheat",
        "growth_stage": "Vegetative",
        "kc_factor": 1.15,
        "size_hectares": 4.5,
        "hour_of_day": 14,
    }
    response = client.post("/api/ml/predict/irrigation", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "irrigation_required" in data
    assert "confidence_score" in data
    assert "model_name" in data


def test_ml_predict_volume_endpoint():
    payload = {
        "field_id": 1,
        "soil_moisture": 22.0,
        "temperature": 32.0,
        "humidity": 40.0,
        "rainfall_1h": 0.0,
        "rainfall_24h": 0.0,
        "rain_probability": 10.0,
        "solar_radiation": 700.0,
        "soil_type": "Clay Loam",
        "crop_type": "Wheat",
        "growth_stage": "Vegetative",
        "kc_factor": 1.15,
        "size_hectares": 4.5,
        "hour_of_day": 14,
    }
    response = client.post("/api/ml/predict/volume", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "predicted_volume_liters" in data
    assert data["predicted_volume_liters"] >= 0


def test_ml_predict_schedule_endpoint():
    payload = {
        "field_id": 1,
        "soil_moisture": 20.0,
        "temperature": 34.0,
        "humidity": 35.0,
        "rainfall_1h": 0.0,
        "rainfall_24h": 0.0,
        "rain_probability": 5.0,
        "solar_radiation": 800.0,
        "soil_type": "Sandy",
        "crop_type": "Cotton",
        "growth_stage": "Flowering",
        "kc_factor": 1.2,
        "size_hectares": 5.0,
        "hour_of_day": 10,
    }
    response = client.post("/api/ml/predict/schedule", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "predicted_volume_liters" in data
    assert "recommended_duration_minutes" in data
    assert "irrigation_required" in data


def test_ml_recommendation_for_field_1():
    response = client.get("/api/ml/recommendation/1")
    assert response.status_code == 200
    data = response.json()
    assert data["field_id"] == 1
    assert "irrigation_required" in data
    assert "predicted_volume_liters" in data
    assert "reason" in data



def test_ml_recommendation_nonexistent_field():
    response = client.get("/api/ml/recommendation/9999")
    assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__])

