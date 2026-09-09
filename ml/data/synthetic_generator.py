"""
ml/data/synthetic_generator.py
Generates realistic 180-day agricultural time-series for training when
real DB data is sparse (cold-start scenario).

Labeling methodology (transparent, documented):
  - irrigation_required: 1 if soil_moisture < 65% of field_capacity AND rain_prob < 40%
  - irrigation_volume_liters: ET0-based formula (see _compute_volume)
  - recommended_hour: 6 (morning) or 18 (evening based on temperature)

All assumptions are configurable via ml/config.py.
"""
import math
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
from typing import Optional

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from ml import config as cfg


def _field_capacity(soil_type: str) -> float:
    key = soil_type.lower().strip()
    for k, v in cfg.FIELD_CAPACITY.items():
        if k in key:
            return v
    return cfg.FIELD_CAPACITY["default"]


def _compute_et0(temp: float, humidity: float, solar_rad: float) -> float:
    """Simplified Hargreaves ET0 approximation (mm/day)."""
    et0 = 0.0023 * (temp + 17.8) * max(0, math.sqrt(abs(temp - (temp * 0.8)))) * solar_rad / 2450
    return max(0.5, min(et0, 10.0))


def _compute_volume(size_ha: float, kc: float, et0: float, days: float) -> float:
    """ET-based irrigation volume estimate (liters)."""
    vol = size_ha * kc * et0 * days * 10000
    return max(cfg.MIN_IRRIGATION_VOLUME_LITERS,
               min(vol, size_ha * cfg.MAX_LITERS_PER_HECTARE))


def generate_synthetic_dataset(
    field_id: int = 1,
    field_size_ha: float = 4.5,
    soil_type: str = "Clay Loam",
    crop_type: str = "Wheat",
    growth_stage: str = "Vegetative",
    kc_factor: float = 1.15,
    latitude: float = 18.5,
    days: int = cfg.SYNTHETIC_DAYS,
    interval_hours: int = cfg.SYNTHETIC_INTERVAL_HOURS,
    seed: int = cfg.RANDOM_SEED,
) -> pd.DataFrame:
    """
    Generate synthetic agricultural time-series data.
    Returns a DataFrame with features AND labeled targets.
    """
    rng = random.Random(seed)
    np.random.seed(seed)

    fc = _field_capacity(soil_type)
    trigger_threshold = fc * cfg.IRRIGATION_TRIGGER_FRACTION

    start_dt = datetime.now(timezone.utc) - timedelta(days=days)
    records = []
    soil_moisture = rng.uniform(trigger_threshold + 5, fc)
    last_irrigation_at: Optional[datetime] = None
    last_irrigation_volume: float = 0.0
    irrigation_count_7d: int = 0
    irr_7d_window: list = []

    planted_date = start_dt - timedelta(days=rng.randint(10, 30))

    for step in range(days * 24 // interval_hours):
        ts = start_dt + timedelta(hours=step * interval_hours)
        hour = ts.hour
        doy = ts.timetuple().tm_yday

        # ── Temperature: diurnal cycle + seasonal ────────────────────────────
        seasonal_offset = 5.0 * math.sin((doy - 80) * 2 * math.pi / 365)
        base_temp = 26.0 - abs(latitude) * 0.1 + seasonal_offset
        temp = base_temp + 7.0 * math.sin((hour - 8) * math.pi / 12.0) + np.random.normal(0, 0.8)
        temp = round(max(5.0, min(50.0, temp)), 2)

        # ── Humidity: inverse of temperature ─────────────────────────────────
        humidity = round(max(15.0, min(95.0, 80.0 - (temp - 20.0) * 2.0 + np.random.normal(0, 2.0))), 1)

        # ── Solar radiation ───────────────────────────────────────────────────
        daylight = max(0.0, math.sin((hour - 6.0) * math.pi / 12.0)) if 6 <= hour <= 18 else 0.0
        solar_rad = round(max(0.0, 850.0 * daylight + np.random.normal(0, 15.0)), 1)

        # ── Rain: episodic weather patterns (mostly dry, periodic rain systems) ──
        day_index = step * interval_hours // 24
        is_rain_day = (day_index % 10 == 0)
        rain_event = is_rain_day and (13 <= hour <= 15) and (rng.random() < 0.65)
        rain_prob = round(rng.uniform(70.0, 95.0) if is_rain_day else rng.uniform(0.0, 20.0), 1)
        rain_1h = round(rng.uniform(3.0, 8.0) if rain_event else 0.0, 2)

        # ── Soil moisture decay / recharge ────────────────────────────────────
        is_daylight = 6 <= hour <= 18
        temp_factor = max(0.6, temp / 28.0)
        hourly_drying = (0.075 * kc_factor * temp_factor) if is_daylight else 0.015
        evap_loss = hourly_drying + np.random.normal(0, 0.003)
        recharge = rain_1h * 0.25  # Infiltration from rain
        soil_moisture = round(max(8.0, min(fc + 2.0, soil_moisture - evap_loss + recharge)), 2)

        # ── Irrigation decision ───────────────────────────────────────────────
        hours_since_last = (
            (ts - last_irrigation_at).total_seconds() / 3600
            if last_irrigation_at else 999.0
        )
        is_stressed = (soil_moisture < trigger_threshold and rain_prob < cfg.RAIN_POSTPONE_THRESHOLD)
        irrigation_needed = is_stressed and (hours_since_last >= cfg.MIN_IRRIGATION_GAP_HOURS)

        if irrigation_needed:
            et0_daily = _compute_et0(temp, humidity, solar_rad)
            days_since_irr = hours_since_last / 24.0
            vol = _compute_volume(field_size_ha, kc_factor, et0_daily, days_since_irr)
            # Deliver water when scheduled (preferred hours or upon critical deficit)
            if hour in [cfg.PREFERRED_IRRIGATION_HOUR_MORNING, cfg.PREFERRED_IRRIGATION_HOUR_EVENING] or (soil_moisture < trigger_threshold - 3.0):
                moisture_increase = rng.uniform(10.0, 14.0)
                soil_moisture = min(fc, soil_moisture + moisture_increase)
                last_irrigation_at = ts
                last_irrigation_volume = vol
                irrigation_count_7d += 1
        else:
            vol = 0.0

        # ── Target: recommended hour ──────────────────────────────────────────
        if temp > cfg.HIGH_TEMP_EVENING_THRESHOLD:
            rec_hour = cfg.PREFERRED_IRRIGATION_HOUR_EVENING
        else:
            rec_hour = cfg.PREFERRED_IRRIGATION_HOUR_MORNING

        # ── Irrigation history rolling ────────────────────────────────────────
        irr_7d_window = [x for x in irr_7d_window if (ts - x[0]).total_seconds() < 7 * 86400]
        if irrigation_needed:
            irr_7d_window.append((ts, vol))
        rolling_7d_vol = sum(v for _, v in irr_7d_window)
        days_since_planted = (ts - planted_date).days

        records.append({
            "timestamp": ts,
            "field_id": field_id,
            # Soil
            "soil_moisture": soil_moisture,
            "temperature_soil": round(temp * 0.85 + np.random.normal(0, 0.5), 2),
            # Weather
            "temperature": temp,
            "humidity": humidity,
            "rainfall_1h": rain_1h,
            "rainfall_24h": round(rain_1h * rng.uniform(0.5, 3.0), 2),
            "rain_probability": rain_prob,
            "solar_radiation": solar_rad,
            # Crop
            "crop_type": crop_type,
            "growth_stage": growth_stage,
            "kc_factor": kc_factor,
            # Field
            "size_hectares": field_size_ha,
            "soil_type": soil_type,
            # Irrigation history
            "prev_irrigation_volume": last_irrigation_volume,
            "hours_since_last_irrigation": round(hours_since_last, 1),
            "rolling_7d_irrigation_liters": round(rolling_7d_vol, 1),
            # Temporal
            "hour_of_day": hour,
            "day_of_week": ts.weekday(),
            "day_of_year": doy,
            "days_since_planted": days_since_planted,
            # ─ Targets ───────────────────────────────────────────────────────
            "irrigation_required": int(irrigation_needed),
            "irrigation_volume_liters": round(vol, 1),
            "recommended_hour": rec_hour,
        })

    df = pd.DataFrame(records)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    return df


if __name__ == "__main__":
    df = generate_synthetic_dataset()
    pos = df["irrigation_required"].sum()
    print(f"Generated {len(df)} rows | Irrigation events: {pos} ({100*pos/len(df):.1f}%)")
    print(df[["timestamp", "soil_moisture", "temperature", "irrigation_required",
              "irrigation_volume_liters"]].tail(10))
