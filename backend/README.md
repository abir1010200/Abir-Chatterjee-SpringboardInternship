# ⚙️ Backend Service — Telemetry Ingestion & REST API (Milestone 1, 2 & 3)

> **FastAPI Telemetry Ingestion, Farmer Authentication, Data Validation, Weather Synchronization & ML Router Microservice**

---

## 🏗️ Architecture Overview

The backend microservice operates on port `8000` (FastAPI) and handles:
1. **Farmer Authentication & Security**: JWT bearer token generation, password hashing (`bcrypt`), and session management (`/api/v1/auth/login`, `/register`, `/me`).
2. **IoT Sensor Ingestion**: Dual REST `POST /api/v1/sensors/readings` & MQTT Mosquitto broker subscriber listening on `farm/+/field/+/sensor/+/reading`.
3. **Weather Synchronization**: OpenWeather adapter with Tomorrow.io fallback and `APScheduler` 30-minute background worker.
4. **Field & Farmer Management**: Relational CRUD APIs and composite registration.
5. **Data Validation & Cleaning**: Statistical Z-score outlier filtering, rate-of-change spike removal, and gap detection.
6. **ML Intelligence Proxy**: Proxies requests to the ML serving engine (`ml.py`).

---

## 📁 Directory Layout

```
backend/
├── app/
│   ├── api/v1/endpoints/      # REST API endpoints (auth, sensors, weather, fields, cleaning, ml, health)
│   ├── core/                  # Settings, CORS middleware, JWT security & structured JSON logging
│   ├── db/                    # SQLAlchemy 2.0 engine, SessionLocal, and init_db/seed_db scripts
│   ├── models/                # Typed ORM models (Farmer, Field, Crop, Sensor, WeatherData, ML Registry)
│   ├── schemas/               # Pydantic v2 schemas with strict validation rules
│   └── services/              # Ingestion, MQTT subscriber worker, weather adapters, cleaning pipeline
├── migrations/                # TimescaleDB DDL initialization scripts
├── scripts/
│   └── simulate_sensors.py    # Physics-informed soil moisture simulator CLI
└── tests/                     # 32 Pytest unit & integration tests
```

---

## 🚀 Running the Backend

```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive FastAPI Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Testing

Run backend tests:
```bash
python -m pytest backend/tests/ -v
```
All 32 tests pass cleanly.
