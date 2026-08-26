# Data Dictionary: Milestone 1 Telemetry & Meteorological Foundation

> **Target Audience**: Data Engineers, ML Engineers (Milestone 2), Backend Developers  
> **Storage Engine**: PostgreSQL 15+ / TimescaleDB (Hypertables on time-series telemetry)

---

## 1. Entity-Relationship Overview

```
[Farmer] 1 ──── N [Field] 1 ──── N [Crop]
                    │  1
                    ├──── N [Sensor] 1 ──── N [SensorReading]
                    ├──── N [WeatherData]
                    └──── N [IrrigationHistory]
```

---

## 2. Table Specifications

### 2.1 Table: `farmers`
Represents the agricultural owner/operator managing one or more sectors.

| Column | Type | Nullable | Constraints | Description |
| :--- | :--- | :---: | :--- | :--- |
| `id` | `INTEGER` | No | PK, Auto-increment | Unique farmer identifier |
| `name` | `VARCHAR(100)` | No | | Full name of farmer |
| `email` | `VARCHAR(100)` | No | UNIQUE, INDEX | Primary contact & login email |
| `phone` | `VARCHAR(30)` | Yes | | Phone/mobile contact |
| `address` | `VARCHAR(255)` | Yes | | Farm location address |
| `created_at` | `TIMESTAMPTZ` | No | Default `NOW()` | Registration timestamp |
| `updated_at` | `TIMESTAMPTZ` | No | Default `NOW()` | Last profile update timestamp |

---

### 2.2 Table: `fields`
Agricultural field boundary profile. Coordinates drive hyper-local weather fetching.

| Column | Type | Nullable | Constraints | Description |
| :--- | :--- | :---: | :--- | :--- |
| `id` | `INTEGER` | No | PK, Auto-increment | Unique field identifier |
| `farmer_id` | `INTEGER` | No | FK `farmers(id)` ON DELETE CASCADE | Linked farmer profile |
| `name` | `VARCHAR(100)` | No | | Field designation (e.g. North Sector 4) |
| `latitude` | `DOUBLE PRECISION`| No | Range $[-90, 90]$ | GPS latitude (Decimal degrees) |
| `longitude` | `DOUBLE PRECISION`| No | Range $[-180, 180]$ | GPS longitude (Decimal degrees) |
| `size_hectares`| `DOUBLE PRECISION`| No | $> 0.0$ | Area in hectares |
| `soil_type` | `VARCHAR(50)` | No | Default `'Loam'` | Soil classification (Clay Loam, Sand, Silt) |
| `created_at` | `TIMESTAMPTZ` | No | Default `NOW()` | Setup timestamp |

---

### 2.3 Table: `crops`
Active crop lifecycle parameters and water requirement coefficients ($K_c$).

| Column | Type | Nullable | Constraints | Description |
| :--- | :--- | :---: | :--- | :--- |
| `id` | `INTEGER` | No | PK, Auto-increment | Unique crop cycle identifier |
| `field_id` | `INTEGER` | No | FK `fields(id)` ON DELETE CASCADE | Linked agricultural field |
| `crop_type` | `VARCHAR(50)` | No | | Crop name (Wheat, Tomato, Maize) |
| `growth_stage`| `VARCHAR(50)` | No | Default `'Initial'` | Stage (Initial, Vegetative, Flowering, Mid, Late, Harvest) |
| `planted_date`| `DATE` | No | Default `CURRENT_DATE`| Planting date |
| `expected_harvest_date`| `DATE` | Yes | | Expected harvest date |
| `kc_factor` | `DOUBLE PRECISION`| No | Default `1.0` ($0.2 - 2.0$) | Crop evapotranspiration coefficient $K_c$ |
| `is_active` | `BOOLEAN` | No | Default `TRUE` | Whether currently actively growing |
| `created_at` | `TIMESTAMPTZ` | No | Default `NOW()` | Record timestamp |

---

### 2.4 Table: `sensors`
Hardware telemetry device catalog and connectivity health tracker.

| Column | Type | Nullable | Constraints | Description |
| :--- | :--- | :---: | :--- | :--- |
| `id` | `VARCHAR(50)` | No | PK | Unique hardware ID (e.g. `SEN-WHEAT-01`) |
| `field_id` | `INTEGER` | No | FK `fields(id)` ON DELETE CASCADE | Assigned field location |
| `sensor_type`| `VARCHAR(50)` | No | Default `'soil_moisture'` | Telemetry modality (Capacitive, FDR, TDR) |
| `model_name` | `VARCHAR(100)`| Yes | | Manufacturer & model string |
| `install_date`| `TIMESTAMPTZ`| No | Default `NOW()` | Physical installation date |
| `status` | `VARCHAR(20)` | No | `'active'`, `'stale'`, `'offline'` | Dynamic connectivity state |
| `battery_level`| `DOUBLE PRECISION`| Yes | Range $[0.0, 100.0]\%$ | Latest battery percentage |
| `last_seen` | `TIMESTAMPTZ` | Yes | | Timestamp of latest ingested reading |
| `created_at` | `TIMESTAMPTZ` | No | Default `NOW()` | Registration timestamp |

---

### 2.5 Table: `sensor_readings` *(TimescaleDB Hypertable)*
High-frequency time-series telemetry representing in-situ soil root-zone state.

| Column | Type | Nullable | Constraints / Index | Description |
| :--- | :--- | :---: | :--- | :--- |
| `id` | `INTEGER` | No | PK, Auto-increment | Sequence identifier |
| `sensor_id` | `VARCHAR(50)` | No | FK `sensors(id)` ON DELETE CASCADE | Source sensor hardware ID |
| `field_id` | `INTEGER` | No | FK `fields(id)` ON DELETE CASCADE | Field location ID |
| `soil_moisture`| `DOUBLE PRECISION`| No | Range $[0.0, 100.0]\%$ | Volumetric soil moisture percentage |
| `temperature_soil`| `DOUBLE PRECISION`| Yes | Range $[-20.0, 70.0]^\circ\text{C}$ | Soil temperature at root depth |
| `battery_level`| `DOUBLE PRECISION`| Yes | Range $[0.0, 100.0]\%$ | Sensor battery level during transmission |
| `timestamp` | `TIMESTAMPTZ` | No | Time-series partition key | UTC telemetry collection timestamp |
| `is_valid` | `BOOLEAN` | No | Default `TRUE` | `FALSE` if flagged as an anomaly/outlier |
| `cleaning_flag`| `VARCHAR(50)`| No | Default `'raw'` | State: `'raw'`, `'validated'`, `'outlier_flagged'` |
| `created_at` | `TIMESTAMPTZ` | No | Default `NOW()` | Ingestion timestamp |

**Indexes & Constraints**:
- `UNIQUE (sensor_id, timestamp)`: Enforces idempotency and prevents duplicate transmissions.
- `INDEX (field_id, timestamp DESC)`: High-performance time-series slicing per field.
- `INDEX (sensor_id, timestamp DESC)`: Fast hardware-specific historical lookups.

---

### 2.6 Table: `weather_data` *(TimescaleDB Hypertable)*
Synchronized meteorological telemetry from OpenWeatherMap & Tomorrow.io.

| Column | Type | Nullable | Constraints / Index | Description |
| :--- | :--- | :---: | :--- | :--- |
| `id` | `INTEGER` | No | PK, Auto-increment | Sequence identifier |
| `field_id` | `INTEGER` | No | FK `fields(id)` ON DELETE CASCADE | Associated field |
| `temperature`| `DOUBLE PRECISION`| No | Degrees Celsius ($^\circ\text{C}$) | Ambient atmospheric dry-bulb temperature |
| `humidity` | `DOUBLE PRECISION`| No | Range $[0.0, 100.0]\%$ | Ambient relative humidity |
| `rainfall_1h`| `DOUBLE PRECISION`| No | Millimeters ($\text{mm}$) | Precipitation observed in last hour |
| `rainfall_24h`| `DOUBLE PRECISION`| No | Millimeters ($\text{mm}$) | Cumulative 24-hour precipitation |
| `rain_probability`| `DOUBLE PRECISION`| No | Range $[0.0, 100.0]\%$ | Forecasted precipitation probability |
| `wind_speed` | `DOUBLE PRECISION`| Yes | Meters/second ($\text{m/s}$) | Wind velocity |
| `solar_radiation`| `DOUBLE PRECISION`| Yes | $\text{W/m}^2$ | Direct/Diffuse global horizontal irradiance |
| `forecast_json`| `TEXT` | Yes | JSON String | 5-day / 3-hour forecast payload |
| `provider` | `VARCHAR(50)` | No | Default `'openweather'` | Source API (`openweather`, `tomorrow_io`, etc.) |
| `timestamp` | `TIMESTAMPTZ` | No | Time-series partition key | Observation timestamp |
| `created_at` | `TIMESTAMPTZ` | No | Default `NOW()` | Ingestion timestamp |

**Indexes**:
- `INDEX (field_id, timestamp DESC)`: Fast alignment with sensor time series.

---

### 2.7 Table: `irrigation_history`
Ground-truth log of water discharge events used as ML training labels.

| Column | Type | Nullable | Constraints / Index | Description |
| :--- | :--- | :---: | :--- | :--- |
| `id` | `INTEGER` | No | PK, Auto-increment | Unique irrigation event ID |
| `field_id` | `INTEGER` | No | FK `fields(id)` ON DELETE CASCADE | Field watered |
| `volume_liters`| `DOUBLE PRECISION`| No | Liters ($\text{L}$) | Total volumetric water applied |
| `start_time` | `TIMESTAMPTZ` | No | INDEX | Pump start timestamp |
| `end_time` | `TIMESTAMPTZ` | Yes | | Pump stop timestamp |
| `duration_minutes`| `INTEGER` | Yes | Minutes | Total active duration |
| `trigger_source`| `VARCHAR(50)` | No | Default `'manual'` | `'manual'`, `'automated_ml'`, `'rule_based'` |
| `status` | `VARCHAR(20)` | No | Default `'completed'` | Event status |
| `notes` | `TEXT` | Yes | | Operational notes |
| `created_at` | `TIMESTAMPTZ` | No | Default `NOW()` | Log creation timestamp |

---

## 3. Milestone 2 ML Feature Matrix Format

The endpoint `GET /api/cleaning/field/{field_id}/ml-dataset` outputs this multi-modal aligned feature vector:

```json
{
  "timestamp": "2026-08-26T22:00:00Z",
  "field_id": 1,
  "soil_moisture": 32.45,
  "temperature_soil": 24.10,
  "air_temperature": 27.50,
  "humidity": 52.0,
  "rainfall_1h": 0.0,
  "rain_probability": 15.0,
  "solar_radiation": 720.0,
  "crop_type": "Wheat (HD-2967)",
  "growth_stage": "Vegetative",
  "kc_factor": 1.15,
  "moisture_deficit": 5.55,
  "irrigation_recommended": false
}
```
