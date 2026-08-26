import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_get_latest_weather_for_field():
    response = client.get("/api/weather/field/1/latest")
    assert response.status_code == 200
    data = response.json()
    assert "temperature" in data
    assert "humidity" in data
    assert "rain_probability" in data
    assert "rainfall_1h" in data
    assert data["field_id"] == 1

def test_sync_weather_for_field():
    response = client.post("/api/weather/field/1/sync")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "temperature" in data
    assert "weather_record_id" in data

def test_get_weather_history_for_field():
    response = client.get("/api/weather/field/1/history?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_weather_nonexistent_field_returns_404():
    response = client.get("/api/weather/field/9999/latest")
    assert response.status_code == 404
