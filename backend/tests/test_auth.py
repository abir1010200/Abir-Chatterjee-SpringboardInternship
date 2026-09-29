import pytest
from fastapi.testclient import TestClient
from backend.main import app

from backend.app.core.security import hash_password
from backend.app.db.session import SessionLocal
from backend.app.models.farmer import Farmer

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_demo_farmers():
    db = SessionLocal()
    try:
        # Ensure Rajesh Patel exists
        rajesh = db.query(Farmer).filter(Farmer.email == "rajesh.patel@agrofarm.io").first()
        if not rajesh:
            rajesh = Farmer(
                name="Rajesh Patel",
                email="rajesh.patel@agrofarm.io",
                phone="+91-98765-43210",
                address="Plot 42, Green Valley Agricultural Zone, Pune, India",
                password_hash=hash_password("krishi123")
            )
            db.add(rajesh)
        else:
            rajesh.password_hash = hash_password("krishi123")

        # Ensure Amit Sharma exists
        amit = db.query(Farmer).filter(Farmer.email == "amit.sharma@farmtech.io").first()
        if not amit:
            amit = Farmer(
                name="Amit Sharma",
                email="amit.sharma@farmtech.io",
                phone="+91-9988776655",
                address="Sector 9, Nashik Agrozones",
                password_hash=hash_password("krishi123")
            )
            db.add(amit)
        else:
            amit.password_hash = hash_password("krishi123")

        db.commit()
    finally:
        db.close()

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
