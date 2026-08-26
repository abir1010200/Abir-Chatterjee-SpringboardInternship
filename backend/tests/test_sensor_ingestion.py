import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from backend.main import app
from backend.app.db.session import SessionLocal
from backend.app.models.sensor_reading import SensorReading
from backend.app.models.sensor import Sensor

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "service" in data

def test_ingest_single_reading_success():
    now_utc = datetime.now(timezone.utc).isoformat()
    payload = {
        "sensor_id": "SEN-WHEAT-01",
        "field_id": 1,
        "soil_moisture": 42.5,
        "temperature_soil": 24.3,
        "battery_level": 97.0,
        "timestamp": now_utc
    }
    response = client.post("/api/sensors/readings", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["is_duplicate"] is False
    assert data["sensor_id"] == "SEN-WHEAT-01"

def test_ingest_duplicate_reading_idempotency():
    ts = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
    payload = {
        "sensor_id": "SEN-WHEAT-02",
        "field_id": 1,
        "soil_moisture": 36.8,
        "temperature_soil": 22.1,
        "battery_level": 92.0,
        "timestamp": ts
    }
    # First ingest
    res1 = client.post("/api/sensors/readings", json=payload)
    assert res1.status_code == 201
    assert res1.json()["status"] == "success"
    assert res1.json()["is_duplicate"] is False

    # Second ingest with identical (sensor_id, timestamp)
    res2 = client.post("/api/sensors/readings", json=payload)
    assert res2.status_code == 201
    assert res2.json()["status"] == "duplicate"
    assert res2.json()["is_duplicate"] is True

def test_ingest_invalid_moisture_range():
    now_utc = datetime.now(timezone.utc).isoformat()
    payload = {
        "sensor_id": "SEN-WHEAT-01",
        "field_id": 1,
        "soil_moisture": 145.0,  # Invalid: > 100%
        "timestamp": now_utc
    }
    response = client.post("/api/sensors/readings", json=payload)
    assert response.status_code == 422

def test_ingest_future_timestamp_rejected():
    future_time = (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
    payload = {
        "sensor_id": "SEN-WHEAT-01",
        "field_id": 1,
        "soil_moisture": 30.0,
        "timestamp": future_time
    }
    response = client.post("/api/sensors/readings", json=payload)
    assert response.status_code == 422

def test_batch_ingest_readings():
    now_utc = datetime.now(timezone.utc)
    batch_payload = {
        "readings": [
            {
                "sensor_id": "SEN-WHEAT-01",
                "field_id": 1,
                "soil_moisture": 35.0,
                "timestamp": (now_utc - timedelta(minutes=15)).isoformat()
            },
            {
                "sensor_id": "SEN-WHEAT-01",
                "field_id": 1,
                "soil_moisture": 34.5,
                "timestamp": (now_utc - timedelta(minutes=10)).isoformat()
            }
        ]
    }
    response = client.post("/api/sensors/readings/batch", json=batch_payload)
    assert response.status_code == 201
    results = response.json()
    assert len(results) == 2
    assert results[0]["status"] == "success"

def test_query_sensor_readings():
    response = client.get("/api/sensors/SEN-WHEAT-01/readings?limit=10")
    assert response.status_code == 200
    readings = response.json()
    assert isinstance(readings, list)
    assert len(readings) > 0
