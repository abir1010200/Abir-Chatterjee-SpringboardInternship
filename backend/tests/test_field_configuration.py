import pytest
from datetime import date
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_composite_field_registration():
    payload = {
        "farmer": {
            "name": "Amit Sharma",
            "email": "amit.sharma@farmtech.io",
            "phone": "+91-9988776655",
            "address": "Sector 9, Nashik Agrozones"
        },
        "field": {
            "name": "Nashik Tomato Sector 1",
            "latitude": 19.9975,
            "longitude": 73.7898,
            "size_hectares": 2.2,
            "soil_type": "Sandy Loam"
        },
        "crop": {
            "crop_type": "Tomato (Hybrid)",
            "growth_stage": "Flowering",
            "planted_date": str(date.today()),
            "kc_factor": 1.25,
            "is_active": True
        },
        "sensor": {
            "sensor_id": "SEN-TOMATO-01",
            "sensor_type": "soil_moisture",
            "model_name": "Capacitive-FDR-Pro"
        }
    }

    response = client.post("/api/fields/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert "field_id" in data
    assert data["sensor_id"] == "SEN-TOMATO-01"

def test_list_fields_returns_records():
    response = client.get("/api/fields")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_update_crop_growth_stage():
    # Update stage of Crop ID 1
    payload = {
        "growth_stage": "Flowering",
        "kc_factor": 1.20
    }
    response = client.put("/api/fields/crops/1", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["growth_stage"] == "Flowering"
    assert data["kc_factor"] == 1.20
