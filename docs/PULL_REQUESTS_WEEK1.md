# Week 1 Pull Request Summaries & Code Reviews

---

## 🔀 PR #1: Development Environment Setup & Monorepo Structure
- **Branch**: `feature/sensor-ingestion` -> `dev`
- **Related Section**: Section 2
- **Summary**:
  - Configured monorepo layout (`/backend`, `/frontend`, `/ml`, `/infra`).
  - Added `docker-compose.yml` with TimescaleDB, Mosquitto MQTT broker, FastAPI backend, and Next.js frontend.
  - Added `.env.example`, `.vscode/settings.json`, and root `.gitignore`.
- **Reviewer Feedback**: Approved with no blocking issues. Environment is cleanly reproducible.

---

## 🔀 PR #2: Database Schema & Time-Series Design
- **Branch**: `feature/sensor-ingestion` -> `dev`
- **Related Section**: Section 3
- **Summary**:
  - Implemented SQLAlchemy 2.0 models for `Farmer`, `Field`, `Crop`, `Sensor`, `SensorReading`, `WeatherData`, and `IrrigationHistory`.
  - Added composite indexes on `(field_id, timestamp)` and `(sensor_id, timestamp)`.
  - Added unique constraint on `(sensor_id, timestamp)` for telemetry deduplication.
  - Created `backend/migrations/init.sql` with TimescaleDB hypertable DDL and `init_db.py` seeding script.
- **Reviewer Feedback**: Verified idempotency constraints and cascade behavior.

---

## 🔀 PR #3: Sensor Telemetry Ingestion (REST & MQTT)
- **Branch**: `feature/sensor-ingestion` -> `dev`
- **Related Section**: Section 4
- **Summary**:
  - Pydantic payload models with physical range validation ($0-100\%$) and timestamp sanity checks.
  - `POST /api/sensors/readings` single and batch ingestion endpoints.
  - Mosquitto MQTT subscriber worker with automatic topic pattern extraction (`farm/+/field/+/sensor/+/reading`).
  - Implemented shared ingestion core with idempotency handling.
  - Pytest test suite covering 7 unit/integration test cases.
- **Reviewer Feedback**: Verified passing test suite with $100\%$ green status.

---

## 🔀 PR #4: Physics-Informed Sensor Data Simulator
- **Branch**: `feature/sensor-ingestion` -> `dev`
- **Related Section**: Section 5
- **Summary**:
  - Created `/backend/scripts/simulate_sensors.py` generating realistic soil drying (diurnal solar curve), evapotranspiration, and infiltration spikes upon irrigation.
  - Supports `--protocol rest`, `--protocol mqtt`, and `--protocol backfill`.
  - Configurable CLI flags for `--fields`, `--sensors-per-field`, `--interval`, `--duration`, and `--historical-days`.
- **Reviewer Feedback**: Backfill successfully populated test database. Ready for merge to `dev`.
