# AI-Powered Smart Irrigation System — Milestone 1

> **Milestone 1**: Data Ingestion, Weather Integration & Soil Moisture Telemetry Pipeline

---

## 🌾 Project Overview
An intelligent, data-driven irrigation management platform designed to eliminate water waste and optimize crop yields. Milestone 1 establishes the real-time telemetry ingestion, meteorological synchronization, crop configuration, and data cleaning engine that feeds downstream machine learning models (Random Forest / LSTM in Milestone 2).

---

## 🏗️ Architecture & Monorepo Structure

```
├── .env.example             # Complete environment variable template
├── .gitignore               # Root git ignore rules
├── .vscode/                 # Recommended VS Code settings & extensions
├── docker-compose.yml       # TimescaleDB, Mosquitto, FastAPI, Next.js
├── backend/                 # FastAPI REST API & Ingestion Engine
│   ├── app/                 # Application source (models, routes, services)
│   ├── migrations/          # SQL migrations (TimescaleDB / Postgres)
│   ├── scripts/             # Sensor simulator & test scripts
│   ├── tests/               # Pytest suite
│   ├── requirements.txt     # Python dependencies
│   └── pyproject.toml       # Backend package metadata
├── frontend/                # Next.js 14 PWA Dashboard
│   ├── src/                 # React components & App Router pages
│   ├── public/              # PWA manifest & static assets
│   ├── package.json         # Node dependencies
│   ├── tailwind.config.js   # Tailwind styling theme
│   └── tsconfig.json        # TypeScript configuration
├── ml/                      # ML exploratory notebooks & feature specs
│   ├── exploratory_data_checks.ipynb
│   └── README.md
└── infra/                   # Dockerfiles & MQTT broker config
    ├── Dockerfile.backend
    ├── Dockerfile.frontend
    └── mosquitto.conf
```

---

## 🚀 Quick Start (Development Environment)

### 1. Prerequisites
- **Python**: 3.10+ (Recommended: 3.11 / 3.14)
- **Node.js**: 18+ (Recommended: 20+)
- **Docker & Docker Compose** (Optional for local containerized stack)

### 2. Configure Environment
```bash
cp .env.example .env
```

### 3. Running with Docker Compose
```bash
docker-compose up --build
```
- **FastAPI Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Next.js PWA Dashboard**: [http://localhost:3000](http://localhost:3000)
- **MQTT Broker**: `localhost:1883`

---

## 📋 Milestone 1 Success Criteria Checklist
- [x] **Project environment configured** (Section 2)
- [x] **GitHub / Git repository created** (Section 2)
- [x] **Database schema completed** (Section 3)
- [ ] **Sensor data ingestion working** (Section 4)
- [ ] **Simulated sensor data available** (Section 5)
- [ ] **Weather API integrated** (Section 7)
- [ ] **Farmer, field, crop, and sensor configuration implemented** (Section 8)
- [ ] **Data validation and cleaning implemented** (Sections 9 & 10)
- [ ] **Historical sensor and weather data stored** (Section 12)
- [ ] **Error handling implemented** (Section 11)
