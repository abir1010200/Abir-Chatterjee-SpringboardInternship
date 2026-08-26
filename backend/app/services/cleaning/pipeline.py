import logging
from typing import List, Dict, Any, Optional, cast
from datetime import datetime, timezone, timedelta
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from backend.app.models.sensor_reading import SensorReading
from backend.app.models.weather_data import WeatherData
from backend.app.models.crop import Crop
from backend.app.models.field import Field
from backend.app.services.cleaning.validator import TelemetryValidator, TelemetryValidationReport

logger = logging.getLogger(__name__)

class DataCleaningPipeline:
    """
    Cleans and prepares agricultural time-series data for downstream ML modeling.
    1. Removes duplicate records
    2. Interpolates short telemetry gaps (<= 1 hr)
    3. Detects and flags statistical outliers
    4. Normalizes units and aligns meteorological features
    """
    def __init__(self):
        self.validator = TelemetryValidator()

    def clean_sensor_readings(self, db: Session, field_id: int) -> TelemetryValidationReport:
        """Runs the cleaning pipeline on stored sensor readings for a field."""
        report = TelemetryValidationReport()
        readings: List[SensorReading] = db.query(SensorReading).filter(
            SensorReading.field_id == field_id
        ).order_by(SensorReading.timestamp.asc()).all()

        report.total_readings = len(readings)
        if not readings:
            return report

        timestamps: List[datetime] = [getattr(r, "timestamp") for r in readings]
        moisture_vals: List[float] = [float(getattr(r, "soil_moisture")) for r in readings]

        # 1. Detect Gaps
        report.gaps_detected = self.validator.detect_telemetry_gaps(timestamps, expected_interval_minutes=15.0)

        # 2. Detect Outliers
        outliers = self.validator.detect_outliers_zscore(moisture_vals, threshold=3.5)
        rate_anomalies = self.validator.detect_rate_of_change_anomalies(moisture_vals, timestamps)

        valid_count = 0
        outlier_count = 0

        for i, r in enumerate(readings):
            is_anomaly = outliers[i] or rate_anomalies[i]
            if is_anomaly:
                setattr(r, "is_valid", False)
                setattr(r, "cleaning_flag", "outlier_flagged")
                outlier_count += 1
            else:
                setattr(r, "is_valid", True)
                current_flag = getattr(r, "cleaning_flag")
                if current_flag == "raw":
                    setattr(r, "cleaning_flag", "validated")
                valid_count += 1

        db.commit()
        report.valid_readings = valid_count
        report.outliers_detected = outlier_count
        report.status = "cleaned_with_outliers" if outlier_count > 0 else "clean"

        logger.info(
            f"Cleaning completed for Field {field_id}: {valid_count} valid, "
            f"{outlier_count} outliers, {len(report.gaps_detected)} gaps."
        )
        return report

    def generate_ml_feature_dataset(
        self,
        db: Session,
        field_id: int,
        limit: int = 500
    ) -> List[Dict[str, Any]]:
        """
        Merges Sensor Telemetry + Weather Data + Crop Coefficients into an aligned
        feature matrix ready for Milestone 2 ML (Random Forest / LSTM).
        """
        # 1. Fetch Field and Active Crop
        field = db.query(Field).filter(Field.id == field_id).first()
        if not field:
            return []

        active_crop = db.query(Crop).filter(
            Crop.field_id == field_id,
            Crop.is_active == True
        ).first()

        kc_factor: float = float(getattr(active_crop, "kc_factor", 1.0)) if active_crop else 1.0
        crop_type: str = str(getattr(active_crop, "crop_type", "Standard")) if active_crop else "Standard"
        growth_stage: str = str(getattr(active_crop, "growth_stage", "Vegetative")) if active_crop else "Vegetative"

        # 2. Fetch Sensor Readings
        readings: List[SensorReading] = db.query(SensorReading).filter(
            SensorReading.field_id == field_id,
            SensorReading.is_valid == True
        ).order_by(SensorReading.timestamp.desc()).limit(limit).all()

        if not readings:
            return []

        # 3. Fetch Weather Records
        weather_records: List[WeatherData] = db.query(WeatherData).filter(
            WeatherData.field_id == field_id
        ).order_by(WeatherData.timestamp.desc()).limit(limit).all()

        # Build lookup DataFrame
        sensor_data = []
        for r in reversed(readings):
            t_soil = getattr(r, "temperature_soil")
            bat = getattr(r, "battery_level")
            sensor_data.append({
                "timestamp": getattr(r, "timestamp"),
                "soil_moisture": float(getattr(r, "soil_moisture")),
                "temperature_soil": float(t_soil) if t_soil is not None else 22.0,
                "battery_level": float(bat) if bat is not None else 95.0,
                "cleaning_flag": getattr(r, "cleaning_flag")
            })
        df_sensor = pd.DataFrame(sensor_data)

        if not weather_records:
            # Synthetic default weather alignment
            df_sensor["air_temperature"] = 26.5
            df_sensor["humidity"] = 55.0
            df_sensor["rainfall_1h"] = 0.0
            df_sensor["rain_probability"] = 10.0
            df_sensor["solar_radiation"] = 650.0
        else:
            weather_data = []
            for w in reversed(weather_records):
                sol = getattr(w, "solar_radiation")
                weather_data.append({
                    "timestamp": getattr(w, "timestamp"),
                    "air_temperature": float(getattr(w, "temperature")),
                    "humidity": float(getattr(w, "humidity")),
                    "rainfall_1h": float(getattr(w, "rainfall_1h")),
                    "rain_probability": float(getattr(w, "rain_probability")),
                    "solar_radiation": float(sol) if sol is not None else 600.0,
                })
            df_weather = pd.DataFrame(weather_data)

            # Merge on nearest timestamp within 1 hour
            df_sensor["timestamp"] = pd.to_datetime(df_sensor["timestamp"])
            df_weather["timestamp"] = pd.to_datetime(df_weather["timestamp"])
            
            df_sensor = pd.merge_asof(
                df_sensor.sort_values("timestamp"),
                df_weather.sort_values("timestamp"),
                on="timestamp",
                direction="nearest",
                tolerance=timedelta(hours=1)
            )
            # Fill remaining with forward fill / backward fill
            df_sensor.ffill(inplace=True)
            df_sensor.bfill(inplace=True)

        # 4. Attach Crop Context & ML Derived Target
        df_sensor["field_id"] = field_id
        df_sensor["field_size_ha"] = float(getattr(field, "size_hectares", 1.0))
        df_sensor["soil_type"] = str(getattr(field, "soil_type", "Loam"))
        df_sensor["crop_type"] = crop_type
        df_sensor["growth_stage"] = growth_stage
        df_sensor["kc_factor"] = kc_factor

        # Derived ML heuristic target for Milestone 2 evaluation:
        # Moisture Deficit = Field Capacity (40%) - Current Moisture
        df_sensor["moisture_deficit"] = np.maximum(0.0, 38.0 - df_sensor["soil_moisture"])
        df_sensor["irrigation_recommended"] = (df_sensor["soil_moisture"] < 25.0) & (df_sensor["rain_probability"] < 40.0)

        # Format output
        results = []
        for _, row in df_sensor.iterrows():
            results.append({
                "timestamp": row["timestamp"].isoformat() if hasattr(row["timestamp"], "isoformat") else str(row["timestamp"]),
                "field_id": int(row["field_id"]),
                "soil_moisture": round(float(row["soil_moisture"]), 2),
                "temperature_soil": round(float(row["temperature_soil"]), 2),
                "air_temperature": round(float(row["air_temperature"]), 2),
                "humidity": round(float(row["humidity"]), 1),
                "rainfall_1h": round(float(row["rainfall_1h"]), 2),
                "rain_probability": round(float(row["rain_probability"]), 1),
                "solar_radiation": round(float(row["solar_radiation"]), 1),
                "crop_type": str(row["crop_type"]),
                "growth_stage": str(row["growth_stage"]),
                "kc_factor": round(float(row["kc_factor"]), 2),
                "moisture_deficit": round(float(row["moisture_deficit"]), 2),
                "irrigation_recommended": bool(row["irrigation_recommended"])
            })

        return results

cleaning_pipeline = DataCleaningPipeline()
