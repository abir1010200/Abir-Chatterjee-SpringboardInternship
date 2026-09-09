"""
ml/data/loader.py
Loads data from the existing Milestone 1 database tables.
Falls back to synthetic data if real data is insufficient.
"""
import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Optional

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from backend.app.db.session import SessionLocal
from backend.app.models.sensor_reading import SensorReading
from backend.app.models.weather_data import WeatherData
from backend.app.models.crop import Crop
from backend.app.models.field import Field
from backend.app.models.irrigation_history import IrrigationHistory
from ml import config as cfg
from ml.data.synthetic_generator import generate_synthetic_dataset

logger = logging.getLogger(__name__)


def load_field_dataset(
    field_id: int,
    db: Optional[Session] = None,
    min_rows: int = cfg.SYNTHETIC_MIN_ROWS,
) -> pd.DataFrame:
    """
    Load ML-ready dataset for a field.
    If real data < min_rows, synthetic data is used (documented fallback).
    """
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        # ── Field info ────────────────────────────────────────────────────────
        field = db.query(Field).filter(Field.id == field_id).first()
        if not field:
            logger.warning(f"Field {field_id} not found — using defaults")
            size_ha = 1.0
            soil_type = "Loam"
            lat = 18.5
        else:
            size_ha = float(field.size_hectares)
            soil_type = str(field.soil_type)
            lat = float(field.latitude)

        # ── Active crop ───────────────────────────────────────────────────────
        crop = db.query(Crop).filter(
            Crop.field_id == field_id, Crop.is_active == True
        ).first()
        crop_type = str(crop.crop_type) if crop else "Unknown"
        growth_stage = str(crop.growth_stage) if crop else "Vegetative"
        kc_factor = float(crop.kc_factor) if crop else 1.0
        planted_date = crop.planted_date if crop else None

        # ── Sensor readings ───────────────────────────────────────────────────
        readings = db.query(SensorReading).filter(
            SensorReading.field_id == field_id,
            SensorReading.is_valid == True,
        ).order_by(SensorReading.timestamp.asc()).all()

        # ── Check if synthetic needed ─────────────────────────────────────────
        if len(readings) < min_rows:
            logger.info(
                f"Field {field_id}: only {len(readings)} real sensor readings "
                f"(< {min_rows} minimum). Using synthetic data generator."
            )
            df = generate_synthetic_dataset(
                field_id=field_id,
                field_size_ha=size_ha,
                soil_type=soil_type,
                crop_type=crop_type,
                growth_stage=growth_stage,
                kc_factor=kc_factor,
                latitude=lat,
            )
            df["data_source"] = "synthetic"
            return df

        # ── Real data path ────────────────────────────────────────────────────
        sensor_rows = []
        for r in readings:
            sensor_rows.append({
                "timestamp": r.timestamp,
                "soil_moisture": float(r.soil_moisture),
                "temperature_soil": float(r.temperature_soil) if r.temperature_soil else None,
            })
        df_sensor = pd.DataFrame(sensor_rows)
        df_sensor["timestamp"] = pd.to_datetime(df_sensor["timestamp"], utc=True)

        # ── Weather data ──────────────────────────────────────────────────────
        weather = db.query(WeatherData).filter(
            WeatherData.field_id == field_id
        ).order_by(WeatherData.timestamp.asc()).all()

        if weather:
            weather_rows = []
            for w_rec in weather:
                forecast = {}
                if w_rec.forecast_json:
                    try:
                        forecast_list = json.loads(w_rec.forecast_json)
                        if forecast_list:
                            forecast = {
                                "forecast_temp_6h": float(forecast_list[0].get("temp", w_rec.temperature)),
                                "forecast_rain_prob_6h": float(forecast_list[0].get("pop", w_rec.rain_probability)),
                            }
                    except Exception:
                        pass
                weather_rows.append({
                    "timestamp": w_rec.timestamp,
                    "temperature": float(w_rec.temperature),
                    "humidity": float(w_rec.humidity),
                    "rainfall_1h": float(w_rec.rainfall_1h),
                    "rainfall_24h": float(w_rec.rainfall_24h),
                    "rain_probability": float(w_rec.rain_probability),
                    "solar_radiation": float(w_rec.solar_radiation) if w_rec.solar_radiation else 500.0,
                    **forecast,
                })
            df_weather = pd.DataFrame(weather_rows)
            df_weather["timestamp"] = pd.to_datetime(df_weather["timestamp"], utc=True)
            df_merged = pd.merge_asof(
                df_sensor.sort_values("timestamp"),
                df_weather.sort_values("timestamp"),
                on="timestamp",
                direction="nearest",
                tolerance=timedelta(hours=1)
            )
            df_merged.ffill(inplace=True)
            df_merged.bfill(inplace=True)
        else:
            df_merged = df_sensor.copy()
            df_merged["temperature"] = 26.5
            df_merged["humidity"] = 55.0
            df_merged["rainfall_1h"] = 0.0
            df_merged["rainfall_24h"] = 0.0
            df_merged["rain_probability"] = 10.0
            df_merged["solar_radiation"] = 600.0

        # ── Irrigation history ────────────────────────────────────────────────
        irr_hist = db.query(IrrigationHistory).filter(
            IrrigationHistory.field_id == field_id,
            IrrigationHistory.status == "completed",
        ).order_by(IrrigationHistory.start_time.asc()).all()

        df_merged["field_id"] = field_id
        df_merged["size_hectares"] = size_ha
        df_merged["soil_type"] = soil_type
        df_merged["crop_type"] = crop_type
        df_merged["growth_stage"] = growth_stage
        df_merged["kc_factor"] = kc_factor

        # ── Label construction (transparent methodology) ──────────────────────
        fc = _field_capacity_for_soil(soil_type)
        trigger = fc * cfg.IRRIGATION_TRIGGER_FRACTION

        df_merged["irrigation_required"] = (
            (df_merged["soil_moisture"] < trigger) &
            (df_merged["rain_probability"] < cfg.RAIN_POSTPONE_THRESHOLD)
        ).astype(int)

        # Volume: use actual history where available
        if irr_hist:
            last_vol = float(irr_hist[-1].volume_liters)
        else:
            last_vol = size_ha * kc_factor * 4.0 * 10000 / 24  # default ET-based
        df_merged["irrigation_volume_liters"] = np.where(
            df_merged["irrigation_required"] == 1, last_vol, 0.0
        )
        df_merged["recommended_hour"] = np.where(
            df_merged["temperature"] > cfg.HIGH_TEMP_EVENING_THRESHOLD,
            cfg.PREFERRED_IRRIGATION_HOUR_EVENING,
            cfg.PREFERRED_IRRIGATION_HOUR_MORNING,
        )

        # ── Irrigation history features ───────────────────────────────────────
        if irr_hist:
            last_irr_time = irr_hist[-1].start_time
            if last_irr_time.tzinfo is None:
                last_irr_time = last_irr_time.replace(tzinfo=timezone.utc)
            df_merged["prev_irrigation_volume"] = float(irr_hist[-1].volume_liters)
            df_merged["prev_irrigation_duration"] = (
                float(irr_hist[-1].duration_minutes) if irr_hist[-1].duration_minutes else 30.0
            )
            df_merged["hours_since_last_irrigation"] = df_merged["timestamp"].apply(
                lambda t: (t - last_irr_time).total_seconds() / 3600 if t >= last_irr_time else 999.0
            )
            df_merged["rolling_7d_irrigation_liters"] = float(
                sum(h.volume_liters for h in irr_hist[-7:])
            )
        else:
            df_merged["prev_irrigation_volume"] = 0.0
            df_merged["prev_irrigation_duration"] = 0.0
            df_merged["hours_since_last_irrigation"] = 999.0
            df_merged["rolling_7d_irrigation_liters"] = 0.0

        if planted_date:
            df_merged["days_since_planted"] = df_merged["timestamp"].apply(
                lambda t: max(0, (t.date() if hasattr(t, "date") else datetime.fromtimestamp(t.timestamp()).date()) - planted_date).days
                if hasattr(planted_date, "__sub__") else 0
            )
        else:
            df_merged["days_since_planted"] = 0

        df_merged["hour_of_day"] = df_merged["timestamp"].dt.hour
        df_merged["day_of_week"] = df_merged["timestamp"].dt.dayofweek
        df_merged["day_of_year"] = df_merged["timestamp"].dt.dayofyear
        df_merged["data_source"] = "real"

        logger.info(f"Field {field_id}: loaded {len(df_merged)} real rows")
        return df_merged

    finally:
        if close_db:
            db.close()


def _field_capacity_for_soil(soil_type: str) -> float:
    key = soil_type.lower().strip()
    for k, v in cfg.FIELD_CAPACITY.items():
        if k in key:
            return v
    return cfg.FIELD_CAPACITY["default"]


def load_all_fields_dataset(min_rows: int = cfg.SYNTHETIC_MIN_ROWS) -> pd.DataFrame:
    """Load and concatenate datasets for all registered fields."""
    db = SessionLocal()
    try:
        fields = db.query(Field).all()
        if not fields:
            logger.info("No fields in DB — generating synthetic for field_id=1")
            return generate_synthetic_dataset()
        dfs = [load_field_dataset(f.id, db=db, min_rows=min_rows) for f in fields]
        return pd.concat(dfs, ignore_index=True)
    finally:
        db.close()
