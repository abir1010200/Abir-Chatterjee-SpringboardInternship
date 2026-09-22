import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_login_demo_farmer_success():
    response = client.post(
        "/api/auth/login",
        json={"username_or_email": "rajesh.patel@agrofarm.io", "password": "krishi123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["farmer"]["email"] == "rajesh.patel@agrofarm.io"
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials():
    response = client.post(
        "/api/auth/login",
        json={"username_or_email": "rajesh.patel@agrofarm.io", "password": "wrong_password_123"}
    )
    assert response.status_code == 401

def test_login_nonexistent_user():
    response = client.post(
        "/api/auth/login",
        json={"username_or_email": "nonexistent@farmer.org", "password": "krishi123"}
    )
    assert response.status_code == 401

def test_get_current_farmer_profile():
    # Login first
    login_res = client.post(
        "/api/auth/login",
        json={"username_or_email": "amit.sharma@farmtech.io", "password": "krishi123"}
    )
    token = login_res.json()["access_token"]

    # Access /me
    me_res = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_res.status_code == 200
    data = me_res.json()
    assert data["success"] is True
    assert data["farmer"]["name"] == "Amit Sharma"

def test_logout_endpoint():
    response = client.post("/api/auth/logout")
    assert response.status_code == 200
    assert response.json()["success"] is True
