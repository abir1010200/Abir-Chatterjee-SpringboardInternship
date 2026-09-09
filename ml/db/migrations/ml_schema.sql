-- =============================================================================
-- Milestone 2: Additive ML Tables
-- These tables are backward-compatible additions to the Milestone 1 schema.
-- No existing tables are modified.
-- =============================================================================

-- 1. ML Model Registry
CREATE TABLE IF NOT EXISTS ml_model_registry (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    task_type VARCHAR(50) NOT NULL DEFAULT 'classification',
    metrics_json TEXT,
    artifact_path TEXT,
    mlflow_run_id VARCHAR(100),
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    trained_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_ml_registry_active ON ml_model_registry(model_name, is_active);

-- 2. Irrigation Predictions Log
CREATE TABLE IF NOT EXISTS irrigation_predictions (
    id SERIAL PRIMARY KEY,
    field_id INTEGER NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL DEFAULT 'unknown',
    prediction_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    irrigation_required BOOLEAN NOT NULL,
    confidence_score DOUBLE PRECISION,
    predicted_volume_liters DOUBLE PRECISION,
    recommended_hour INTEGER,
    recommended_duration_minutes INTEGER,
    risk_level VARCHAR(20) DEFAULT 'MEDIUM',
    reason TEXT,
    soil_moisture_context DOUBLE PRECISION,
    temperature_context DOUBLE PRECISION,
    rain_probability_context DOUBLE PRECISION,
    crop_type VARCHAR(50),
    growth_stage VARCHAR(50),
    schedule_json TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_predictions_field_time ON irrigation_predictions(field_id, prediction_timestamp DESC);

-- 3. Irrigation Schedules
CREATE TABLE IF NOT EXISTS irrigation_schedules (
    id SERIAL PRIMARY KEY,
    prediction_id INTEGER REFERENCES irrigation_predictions(id) ON DELETE SET NULL,
    field_id INTEGER NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    scheduled_date DATE NOT NULL,
    recommended_start_time TIME,
    duration_minutes INTEGER,
    volume_liters DOUBLE PRECISION,
    priority VARCHAR(20) DEFAULT 'MEDIUM',
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_schedules_field_date ON irrigation_schedules(field_id, scheduled_date DESC);
