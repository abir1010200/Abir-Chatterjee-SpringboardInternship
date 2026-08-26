-- =============================================================================
-- AI-Powered Smart Irrigation System - Database Schema Migration
-- Compatible with PostgreSQL 14+ and TimescaleDB
-- =============================================================================

-- Optional: Enable TimescaleDB extension if available
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- 1. Farmers Table
CREATE TABLE IF NOT EXISTS farmers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(30),
    address VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. Fields Table
CREATE TABLE IF NOT EXISTS fields (
    id SERIAL PRIMARY KEY,
    farmer_id INTEGER NOT NULL REFERENCES farmers(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    size_hectares DOUBLE PRECISION NOT NULL,
    soil_type VARCHAR(50) NOT NULL DEFAULT 'Loam',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_fields_farmer_id ON fields(farmer_id);

-- 3. Crops Table
CREATE TABLE IF NOT EXISTS crops (
    id SERIAL PRIMARY KEY,
    field_id INTEGER NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    crop_type VARCHAR(50) NOT NULL,
    growth_stage VARCHAR(50) NOT NULL DEFAULT 'Initial',
    planted_date DATE NOT NULL DEFAULT CURRENT_DATE,
    expected_harvest_date DATE,
    kc_factor DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_crops_field_id ON crops(field_id);

-- 4. Sensors Table
CREATE TABLE IF NOT EXISTS sensors (
    id VARCHAR(50) PRIMARY KEY,
    field_id INTEGER NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    sensor_type VARCHAR(50) NOT NULL DEFAULT 'soil_moisture',
    model_name VARCHAR(100) DEFAULT 'Capacitive-FDR-v2',
    install_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    battery_level DOUBLE PRECISION DEFAULT 100.0,
    last_seen TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_sensors_field_id ON sensors(field_id);

-- 5. Sensor Readings Table (Time-Series)
CREATE TABLE IF NOT EXISTS sensor_readings (
    id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(50) NOT NULL REFERENCES sensors(id) ON DELETE CASCADE,
    field_id INTEGER NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    soil_moisture DOUBLE PRECISION NOT NULL,
    temperature_soil DOUBLE PRECISION,
    battery_level DOUBLE PRECISION,
    timestamp TIMESTAMPTZ NOT NULL,
    is_valid BOOLEAN NOT NULL DEFAULT TRUE,
    cleaning_flag VARCHAR(50) NOT NULL DEFAULT 'raw',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_sensor_timestamp UNIQUE (sensor_id, timestamp)
);
CREATE INDEX IF NOT EXISTS idx_sensor_readings_field_time ON sensor_readings(field_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_sensor_readings_sensor_time ON sensor_readings(sensor_id, timestamp DESC);

-- 6. Weather Data Table (Time-Series)
CREATE TABLE IF NOT EXISTS weather_data (
    id SERIAL PRIMARY KEY,
    field_id INTEGER NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    temperature DOUBLE PRECISION NOT NULL,
    humidity DOUBLE PRECISION NOT NULL,
    rainfall_1h DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    rainfall_24h DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    rain_probability DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    wind_speed DOUBLE PRECISION,
    solar_radiation DOUBLE PRECISION,
    forecast_json TEXT,
    provider VARCHAR(50) NOT NULL DEFAULT 'openweather',
    timestamp TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_weather_field_time ON weather_data(field_id, timestamp DESC);

-- 7. Irrigation History Table
CREATE TABLE IF NOT EXISTS irrigation_history (
    id SERIAL PRIMARY KEY,
    field_id INTEGER NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    volume_liters DOUBLE PRECISION NOT NULL,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,
    duration_minutes INTEGER,
    trigger_source VARCHAR(50) NOT NULL DEFAULT 'manual',
    status VARCHAR(20) NOT NULL DEFAULT 'completed',
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_irrigation_field_time ON irrigation_history(field_id, start_time DESC);

-- Conditional TimescaleDB Hypertables
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'timescaledb') THEN
        -- Convert sensor_readings and weather_data into TimescaleDB hypertables
        BEGIN
            PERFORM create_hypertable('sensor_readings', 'timestamp', if_not_exists => TRUE, migrate_data => TRUE);
            PERFORM create_hypertable('weather_data', 'timestamp', if_not_exists => TRUE, migrate_data => TRUE);
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Timescale hypertable setup skipped or already exists.';
        END;
    END IF;
END
$$;
