"""
ml/optimization/scheduler.py
Irrigation optimization engine.
Converts raw ML predictions into actionable, agronomic, conflict-free schedules.
"""
import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timezone, timedelta, date as date_type
from typing import Dict, Any, Optional, Tuple

from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from ml import config as cfg
from ml.db.models import IrrigationPrediction, IrrigationSchedule

logger = logging.getLogger(__name__)


class IrrigationScheduler:
    """
    Translates ML model predictions into actionable field irrigation schedules,
    factoring in soil physics, diurnal solar cycles, and pump constraints.
    """

    DEFAULT_PUMP_FLOW_RATE_LPM: float = 60.0  # 60 Liters per minute standard drip/sprinkler

    def __init__(self, pump_flow_rate_lpm: float = DEFAULT_PUMP_FLOW_RATE_LPM):
        self.flow_rate = pump_flow_rate_lpm

    def calculate_duration(self, volume_liters: float) -> int:
        """Calculate recommended run time in minutes, bounded by safety limits."""
        if volume_liters <= 0:
            return 0
        raw_minutes = volume_liters / self.flow_rate
        return int(max(15, min(raw_minutes, 240)))

    def evaluate_risk_level(
        self,
        soil_moisture: float,
        threshold: float,
        rain_probability: float,
    ) -> Tuple[str, str]:
        """
        Assess agronomic water stress risk and provide natural-language justification.
        Returns: (risk_level, explanation)
        """
        deficit = threshold - soil_moisture

        if deficit > 10.0 and rain_probability < 30.0:
            risk = "CRITICAL"
            reason = (
                f"Severe soil moisture deficit ({deficit:.1f}% below field capacity trigger). "
                f"Low rain probability ({rain_probability:.0f}%). Immediate irrigation required to prevent wilting."
            )
        elif deficit > 0.0 and rain_probability < 40.0:
            risk = "HIGH"
            reason = (
                f"Soil moisture ({soil_moisture:.1f}%) is below optimal threshold ({threshold:.1f}%). "
                f"Rain probability is {rain_probability:.0f}%. Scheduled irrigation advised."
            )
        elif rain_probability >= cfg.RAIN_POSTPONE_THRESHOLD:
            risk = "LOW"
            reason = (
                f"Significant rainfall anticipated ({rain_probability:.0f}%). "
                f"Postponing irrigation to conserve water and prevent waterlogging."
            )
        else:
            risk = "LOW"
            reason = (
                f"Soil moisture ({soil_moisture:.1f}%) is adequate relative to field capacity ({threshold:.1f}%). "
                f"No immediate irrigation needed."
            )

        return risk, reason

    def determine_optimal_slot(
        self,
        recommended_hour: Optional[int],
        temperature: float,
        base_datetime: Optional[datetime] = None,
    ) -> datetime:
        """Determine specific calendar start timestamp minimizing evaporative loss."""
        now = base_datetime or datetime.now(timezone.utc)

        if recommended_hour is not None and 0 <= recommended_hour <= 23:
            hour = recommended_hour
        else:
            hour = (
                cfg.PREFERRED_IRRIGATION_HOUR_EVENING
                if temperature > cfg.HIGH_TEMP_EVENING_THRESHOLD
                else cfg.PREFERRED_IRRIGATION_HOUR_MORNING
            )

        start_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        # If the target hour today has already passed, schedule for tomorrow
        if start_time <= now:
            start_time += timedelta(days=1)

        return start_time

    def generate_schedule(
        self,
        field_id: int,
        prediction_result: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        db: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """
        Assemble comprehensive schedule, assess priority, and persist to database.
        """
        ctx = context or {}
        soil_moisture = float(ctx.get("soil_moisture", 25.0))
        soil_type = str(ctx.get("soil_type", "Loam")).lower()
        rain_prob = float(ctx.get("rain_probability", 10.0))
        temperature = float(ctx.get("temperature", 28.0))
        crop_type = str(ctx.get("crop_type", "Tomato"))
        growth_stage = str(ctx.get("growth_stage", "Vegetative"))

        fc = next((v for k, v in cfg.FIELD_CAPACITY.items() if k in soil_type), cfg.FIELD_CAPACITY["default"])
        trigger_threshold = fc * cfg.IRRIGATION_TRIGGER_FRACTION

        required = bool(prediction_result.get("irrigation_required", False))
        volume = float(prediction_result.get("predicted_volume_liters", 0.0)) if required else 0.0
        confidence = float(prediction_result.get("confidence_score", 0.8))
        model_name = str(prediction_result.get("model_name", "smart_irrigation_ensemble"))
        model_version = str(prediction_result.get("model_version", "1.0.0"))
        rec_hour = prediction_result.get("recommended_hour")

        duration_mins = self.calculate_duration(volume) if required else 0
        risk_level, reason = self.evaluate_risk_level(soil_moisture, trigger_threshold, rain_prob)

        # Priority calculation
        if risk_level == "CRITICAL":
            priority = "CRITICAL"
        elif risk_level == "HIGH":
            priority = "HIGH"
        elif required:
            priority = "MEDIUM"
        else:
            priority = "LOW"

        start_time = self.determine_optimal_slot(rec_hour, temperature) if required else None
        scheduled_date = (start_time.date() if start_time else datetime.now(timezone.utc).date())

        # Soil health status text
        if soil_moisture >= 85.0:
            soil_status = "Saturated (Over-Wet)"
        elif soil_moisture >= trigger_threshold:
            soil_status = "Optimal Moisture"
        elif soil_moisture >= trigger_threshold - 8.0:
            soil_status = "Slightly Dry (Monitor)"
        else:
            soil_status = "Needs Irrigation (Dry)"

        # Pump runtime formatting
        if duration_mins >= 60:
            hrs = duration_mins // 60
            mins = duration_mins % 60
            pump_duration = f"{hrs} hr {mins} mins" if mins > 0 else f"{hrs} hours"
        else:
            pump_duration = f"{duration_mins} minutes"

        # Action badge & farmer advice strings
        if rain_prob >= cfg.RAIN_POSTPONE_THRESHOLD:
            action_badge = "🌧️ RAIN EXPECTED — HOLD WATERING"
            farmer_summary = (
                f"Rain forecast is {rain_prob:.0f}%. Holding irrigation to save electricity and prevent root waterlogging for your {crop_type} ({growth_stage})."
            )
            saving_tip = "💡 Holding watering during rain saves ~₹150-₹300 in electricity and prevents nutrient leaching."
        elif required:
            time_str = start_time.strftime("%I:%M %p") if start_time else "Early Morning"
            action_badge = f"💧 WATER TODAY ({time_str})"
            farmer_summary = (
                f"Water your {crop_type} ({growth_stage}) field at {time_str} with {round(volume):,} Liters of water ({pump_duration} pump time)."
            )
            saving_tip = "💡 Watering in cool morning hours (6 AM - 8 AM) reduces evaporation loss by up to 25%."
        else:
            action_badge = "🌱 OPTIMAL SOIL — NO WATER NEEDED"
            farmer_summary = (
                f"Your {crop_type} field has healthy soil moisture ({soil_moisture:.1f}%). No irrigation is required today."
            )
            saving_tip = "💡 Optimal moisture level maintains healthy root aeration and saves energy."

        schedule_plan = {
            "field_id": field_id,
            "irrigation_required": required,
            "confidence_score": round(confidence, 3),
            "predicted_volume_liters": round(volume, 1),
            "recommended_duration_minutes": duration_mins,
            "recommended_start_time": start_time.isoformat() if start_time else None,
            "priority": priority,
            "risk_level": risk_level,
            "reason": reason,
            "farmer_summary": farmer_summary,
            "action_badge": action_badge,
            "water_saving_tip": saving_tip,
            "soil_health_status": soil_status,
            "pump_duration_display": pump_duration,
            "agronomic_context": {
                "soil_moisture": soil_moisture,
                "field_capacity_trigger": round(trigger_threshold, 1),
                "soil_type": soil_type.title(),
                "crop_type": crop_type,
                "growth_stage": growth_stage,
                "rain_probability": rain_prob,
                "temperature": temperature,
            },
            "model_metadata": {
                "model_name": model_name,
                "model_version": model_version,
            },
        }

        # Optional DB persistence
        if db is not None:
            try:
                db_prediction = IrrigationPrediction(
                    field_id=field_id,
                    model_name=model_name,
                    model_version=model_version,
                    prediction_timestamp=datetime.now(timezone.utc),
                    irrigation_required=required,
                    confidence_score=confidence,
                    predicted_volume_liters=volume,
                    recommended_hour=start_time.hour if start_time else None,
                    recommended_duration_minutes=duration_mins,
                    risk_level=risk_level,
                    reason=reason,
                    soil_moisture_context=soil_moisture,
                    temperature_context=temperature,
                    rain_probability_context=rain_prob,
                    crop_type=crop_type,
                    growth_stage=growth_stage,
                    schedule_json=json.dumps(schedule_plan),
                )
                db.add(db_prediction)
                db.flush()

                if required and start_time is not None:
                    db_schedule = IrrigationSchedule(
                        prediction_id=db_prediction.id,
                        field_id=field_id,
                        scheduled_date=scheduled_date,
                        recommended_start_time=start_time,
                        duration_minutes=duration_mins,
                        volume_liters=volume,
                        priority=priority,
                        status="scheduled",
                    )
                    db.add(db_schedule)

                db.commit()
                schedule_plan["prediction_id"] = int(getattr(db_prediction, "id"))
                logger.info(f"Persisted prediction #{db_prediction.id} for field #{field_id}")
            except Exception as e:
                logger.error(f"Error persisting irrigation schedule to database: {e}")
                db.rollback()

        return schedule_plan
