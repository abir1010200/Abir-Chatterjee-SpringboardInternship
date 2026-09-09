"""
backend/app/api/v1/endpoints/ml.py
REST API endpoints for Machine Learning Irrigation Intelligence & Predictive Scheduling.
"""
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.field import Field
from backend.app.models.crop import Crop
from backend.app.models.sensor_reading import SensorReading
from backend.app.models.weather_data import WeatherData

from ml.serving.schemas import (
    IrrigationPredictRequest,
    IrrigationPredictResponse,
    VolumePredictResponse,
    ScheduleResponse,
    ModelInfoResponse,
    HealthResponse,
)
from ml.serving.model_loader import load_active_model, ServedModelWrapper
from ml.optimization.scheduler import IrrigationScheduler

router = APIRouter()
_active_model_cache: Optional[ServedModelWrapper] = None
scheduler = IrrigationScheduler()


def get_active_model() -> ServedModelWrapper:
    global _active_model_cache
    if _active_model_cache is None:
        _active_model_cache = load_active_model()
    return _active_model_cache


@router.get("/health", response_model=HealthResponse)
def get_ml_health():
    """Liveness probe reporting ML engine status and active model."""
    model = get_active_model()
    return HealthResponse(
        status="healthy",
        service="ml-irrigation-serving",
        model_loaded=model is not None,
        active_model=model.model_name,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/model/info", response_model=ModelInfoResponse)
def get_model_info():
    """Returns active champion model metadata, versioning, and validation metrics."""
    model = get_active_model()
    return ModelInfoResponse(
        active_model=model.model_name,
        version=model.version,
        metrics=model.metrics,
        trained_at=model.trained_at,
        artifact_path=model.artifact_path,
    )


@router.post("/predict/irrigation", response_model=IrrigationPredictResponse)
def predict_irrigation(request: IrrigationPredictRequest):
    """Predict binary irrigation requirement for specified feature vector."""
    model = get_active_model()
    feat_dict = request.model_dump()
    req, vol, conf, _ = model.predict_features(feat_dict)
    return IrrigationPredictResponse(
        irrigation_required=req,
        confidence_score=conf,
        model_name=model.model_name,
        model_version=model.version,
    )


@router.post("/predict/volume", response_model=VolumePredictResponse)
def predict_volume(request: IrrigationPredictRequest):
    """Predict recommended irrigation water delivery volume in Liters."""
    model = get_active_model()
    feat_dict = request.model_dump()
    _, vol, conf, _ = model.predict_features(feat_dict)
    return VolumePredictResponse(
        predicted_volume_liters=vol,
        confidence_score=conf,
        model_name=model.model_name,
        model_version=model.version,
    )


@router.post("/predict/schedule", response_model=ScheduleResponse)
def predict_schedule(request: IrrigationPredictRequest):
    """Generate scheduled irrigation dispatch recommendation with rain constraints."""
    model = get_active_model()
    feat_dict = request.model_dump()
    req, vol, conf, rec_hour = model.predict_features(feat_dict)

    prediction_result = {
        "irrigation_required": req,
        "predicted_volume_liters": vol,
        "confidence_score": conf,
        "recommended_hour": rec_hour,
        "model_name": model.model_name,
        "model_version": model.version,
    }

    schedule_plan = scheduler.generate_schedule(
        field_id=request.field_id or 1,
        prediction_result=prediction_result,
        context=feat_dict,
        db=None,
    )
    return ScheduleResponse(**schedule_plan)


@router.get("/recommendation/{field_id}", response_model=ScheduleResponse)
def get_field_recommendation(field_id: int, db: Session = Depends(get_db)):
    """
    Fetch real-time field telemetry and weather from DB, run ML inference,
    generate schedule, and persist recommendation.
    """
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail=f"Field {field_id} not found.")

    crop = db.query(Crop).filter(Crop.field_id == field_id, Crop.is_active == True).first()
    crop_type = str(getattr(crop, "crop_type", "Tomato")) if crop else "Tomato"
    growth_stage = str(getattr(crop, "growth_stage", "Vegetative")) if crop else "Vegetative"
    kc_factor = float(getattr(crop, "kc_factor", 1.0) or 1.0) if crop else 1.0

    reading = (
        db.query(SensorReading)
        .filter(SensorReading.field_id == field_id, SensorReading.is_valid == True)
        .order_by(SensorReading.timestamp.desc())
        .first()
    )
    soil_moisture = float(getattr(reading, "soil_moisture", 26.0) or 26.0) if reading else 26.0

    weather = (
        db.query(WeatherData)
        .filter(WeatherData.field_id == field_id)
        .order_by(WeatherData.timestamp.desc())
        .first()
    )
    temp = float(getattr(weather, "temperature", 27.5) or 27.5) if weather else 27.5
    humidity = float(getattr(weather, "humidity", 55.0) or 55.0) if weather else 55.0
    rain_prob = float(getattr(weather, "rain_probability", 12.0) or 12.0) if weather else 12.0
    rainfall_1h = float(getattr(weather, "rainfall_1h", 0.0) or 0.0) if weather else 0.0
    solar_rad = float(getattr(weather, "solar_radiation", 650.0) or 650.0) if weather else 650.0
    size_ha = float(getattr(field, "size_hectares", 1.0) or 1.0)

    feat_dict = {
        "field_id": field_id,
        "soil_moisture": soil_moisture,
        "temperature": temp,
        "humidity": humidity,
        "rainfall_1h": rainfall_1h,
        "rainfall_24h": 0.0,
        "rain_probability": rain_prob,
        "solar_radiation": solar_rad,
        "soil_type": str(getattr(field, "soil_type", "Clay Loam")),
        "crop_type": crop_type,
        "growth_stage": growth_stage,
        "kc_factor": kc_factor,
        "size_hectares": size_ha,
        "hour_of_day": datetime.now(timezone.utc).hour,
    }

    model = get_active_model()
    req, vol, conf, rec_hour = model.predict_features(feat_dict)

    prediction_result = {
        "irrigation_required": req,
        "predicted_volume_liters": vol,
        "confidence_score": conf,
        "recommended_hour": rec_hour,
        "model_name": model.model_name,
        "model_version": model.version,
    }

    schedule_plan = scheduler.generate_schedule(
        field_id=field_id,
        prediction_result=prediction_result,
        context=feat_dict,
        db=db,
    )

    return ScheduleResponse(**schedule_plan)
