import sys
from pathlib import Path
ROOT = Path("d:/AbirchatterjeeprojectAI").resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health():
    res = client.get("/api/health/")
    print("Health response:", res.status_code, res.json())
    assert res.status_code == 200

def test_fields():
    res = client.get("/api/fields/")
    print("Fields response:", res.status_code, len(res.json()))
    assert res.status_code == 200

def test_irrigation_history():
    res = client.get("/api/fields/irrigation/history/all")
    print("Irrigation history response:", res.status_code, len(res.json()))
    assert res.status_code == 200

if __name__ == "__main__":
    test_health()
    test_fields()
    test_irrigation_history()
    print("All backend API verification tests passed successfully!")
