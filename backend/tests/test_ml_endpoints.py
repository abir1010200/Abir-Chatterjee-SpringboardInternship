"""
backend/tests/test_ml_endpoints.py
Integration tests for FastAPI ML prediction & schedule recommendation endpoints.
"""
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.main import app

client = TestClient(app)


def test_ml_health_endpoint():
    """Test GET /api/ml/health liveness probe."""
    response = client.get("/api/ml/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data


def test_ml_model_info_endpoint():
    """Test GET /api/ml/model/info endpoint."""
    response = client.get("/api/ml/model/info")
    assert response.status_code == 200
    data = response.json()
    assert "active_model" in data
    assert "version" in data


def test_predict_irrigation_endpoint():
    """Test POST /api/ml/predict/irrigation binary prediction."""
    payload = {
        "field_id": 1,
        "soil_moisture": 22.0,
        "temperature": 32.0,
        "humidity": 45.0,
        "rainfall_1h": 0.0,
        "rain_probability": 5.0,
        "soil_type": "Clay Loam",
        "crop_type": "Wheat",
        "growth_stage": "Vegetative",
        "kc_factor": 1.15,
        "size_hectares": 4.5,
    }
    response = client.post("/api/ml/predict/irrigation", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "irrigation_required" in data
    assert "confidence_score" in data
    assert "model_name" in data


def test_predict_schedule_endpoint():
    """Test POST /api/ml/predict/schedule full schedule recommendation."""
    payload = {
        "field_id": 1,
        "soil_moisture": 18.5,
        "temperature": 34.0,
        "humidity": 40.0,
        "rainfall_1h": 0.0,
        "rain_probability": 10.0,
        "soil_type": "Clay Loam",
        "crop_type": "Wheat",
        "growth_stage": "Flowering",
        "kc_factor": 1.2,
        "size_hectares": 3.0,
    }
    response = client.post("/api/ml/predict/schedule", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["field_id"] == 1
    assert "irrigation_required" in data
    assert "predicted_volume_liters" in data
    assert "priority" in data
    assert "risk_level" in data


def test_get_field_recommendation_endpoint():
    """Test GET /api/ml/recommendation/{field_id} database integration."""
    response = client.get("/api/ml/recommendation/1")
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert data["field_id"] == 1
        assert "agronomic_context" in data

