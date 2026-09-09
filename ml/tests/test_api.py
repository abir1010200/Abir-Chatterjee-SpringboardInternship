"""
ml/tests/test_api.py
API integration tests for FastAPI ML serving endpoints.
"""
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from ml.serving.api import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "active_model" in data
    assert data["model_loaded"] is True


def test_model_info_endpoint():
    response = client.get("/model/info")
    assert response.status_code == 200
    data = response.json()
    assert "active_model" in data
    assert "version" in data


def test_predict_irrigation_endpoint():
    payload = {
        "soil_moisture": 18.5,
        "temperature": 32.0,
        "humidity": 45.0,
        "rainfall_1h": 0.0,
        "rainfall_24h": 0.0,
        "rain_probability": 10.0,
        "solar_radiation": 750.0,
        "soil_type": "Sandy Loam",
        "crop_type": "Tomato",
        "growth_stage": "Flowering",
        "kc_factor": 1.15,
        "size_hectares": 1.5,
    }
    response = client.post("/predict/irrigation", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "irrigation_required" in data
    assert isinstance(data["irrigation_required"], bool)
    assert 0.0 <= data["confidence_score"] <= 1.0


def test_predict_volume_endpoint():
    payload = {
        "soil_moisture": 15.0,
        "temperature": 34.0,
        "humidity": 40.0,
        "rainfall_1h": 0.0,
        "rain_probability": 5.0,
        "size_hectares": 2.0,
        "kc_factor": 1.2,
    }
    response = client.post("/predict/volume", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "predicted_volume_liters" in data
    assert data["predicted_volume_liters"] >= 0.0


def test_predict_schedule_endpoint():
    payload = {
        "soil_moisture": 14.0,
        "temperature": 33.0,
        "humidity": 42.0,
        "rainfall_1h": 0.0,
        "rain_probability": 15.0,
        "size_hectares": 1.0,
        "kc_factor": 1.0,
        "soil_type": "Loam",
        "crop_type": "Wheat",
    }
    response = client.post("/predict/schedule", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "priority" in data
    assert "risk_level" in data
    assert "reason" in data
    assert "agronomic_context" in data
