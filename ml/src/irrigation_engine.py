"""
ml/src/irrigation_engine.py
Irrigation Prediction Engine Module.
Connects trained ML champion models with the IrrigationScheduler to:
1. Predict whether irrigation is required (classification).
2. Predict required water volume (liters) and duration (minutes).
3. Incorporate weather forecast, rain postponement, crop growth stage, and irrigation history.
4. Enforce over-watering guards (soil saturation check, 24h volume caps).
5. Generate time-slotted field-specific irrigation schedules and persist to database.
"""
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from ml import config as cfg
from ml.serving.model_loader import load_active_model, ServedModelWrapper
from ml.optimization.scheduler import IrrigationScheduler
from ml.src.features import extract_features

logger = logging.getLogger(__name__)


class IrrigationPredictionEngine:
    """
    Main entry point for ML-driven predictive irrigation scheduling.
    """

    def __init__(self, model_wrapper: Optional[ServedModelWrapper] = None):
        self.model = model_wrapper or load_active_model()
        self.scheduler = IrrigationScheduler()

    def predict_and_schedule(
        self,
        field_id: int,
        telemetry_context: Dict[str, Any],
        db: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """
        Runs feature engineering, model inference, safety guard evaluation,
        and schedule generation.
        """
        req, vol, conf, rec_hour = self.model.predict_features(telemetry_context)

        prediction_result = {
            "irrigation_required": req,
            "predicted_volume_liters": vol,
            "confidence_score": conf,
            "recommended_hour": rec_hour,
            "model_name": self.model.model_name,
            "model_version": self.model.version,
        }

        # Apply over-watering prevention guards
        soil_moisture = float(telemetry_context.get("soil_moisture", 25.0))
        fc = float(telemetry_context.get("field_capacity", 35.0))
        
        # Guard 1: Saturation check (don't over-irrigate past field capacity)
        if req and soil_moisture >= fc:
            logger.info(f"Field {field_id}: Soil moisture ({soil_moisture}%) >= Field Capacity ({fc}%). Overriding irrigation requirement.")
            prediction_result["irrigation_required"] = False
            prediction_result["predicted_volume_liters"] = 0.0

        # Guard 2: Rain postponement guard
        rain_prob = float(telemetry_context.get("rain_probability", 0.0))
        if req and rain_prob >= cfg.RAIN_POSTPONE_THRESHOLD:
            logger.info(f"Field {field_id}: Rain probability ({rain_prob}%) >= threshold ({cfg.RAIN_POSTPONE_THRESHOLD}%). Postponing irrigation.")
            prediction_result["irrigation_required"] = False
            prediction_result["predicted_volume_liters"] = 0.0

        # Generate schedule plan and optionally persist to DB
        schedule_plan = self.scheduler.generate_schedule(
            field_id=field_id,
            prediction_result=prediction_result,
            context=telemetry_context,
            db=db,
        )

        return schedule_plan
