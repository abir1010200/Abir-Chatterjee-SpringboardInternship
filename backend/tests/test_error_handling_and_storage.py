import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from backend.main import app
from backend.app.db.session import SessionLocal
from backend.app.models.sensor import Sensor

client = TestClient(app)

def test_fleet_health_monitoring():
    response = client.get("/api/sensors/monitoring/health")
    assert response.status_code == 200
    data = response.json()
    assert "total_sensors" in data
    assert "active_count" in data
    assert "stale_count" in data
    assert "offline_count" in data
    assert "sensors" in data
    assert data["total_sensors"] >= 1

def test_historical_time_series_query_last_30_days():
    response = client.get("/api/sensors/field/1/history?days=30&limit=50")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        first = data[0]
        assert "soil_moisture" in first
        assert "timestamp" in first
        assert first["field_id"] == 1

def test_malformed_payload_error_handling():
    # Sending string where float is expected
    payload = {
        "sensor_id": "SEN-WHEAT-01",
        "field_id": 1,
        "soil_moisture": "not_a_number",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    response = client.post("/api/sensors/readings", json=payload)
    assert response.status_code == 422
    err = response.json()
    assert "detail" in err
