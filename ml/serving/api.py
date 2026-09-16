"""
ml/serving/api.py
FastAPI Serving Application for ML Smart Irrigation Engine.
Operates on port 8001 (isolated from main API on port 8000).
"""
import sys
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, cast

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from backend.app.db.session import SessionLocal, get_db
from backend.app.models.field import Field
from backend.app.models.crop import Crop
from backend.app.models.sensor_reading import SensorReading
from backend.app.models.weather_data import WeatherData
from ml import config as cfg
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

logger = logging.getLogger("ml.serving.api")

# Global served model cache
active_model: ServedModelWrapper = load_active_model()
scheduler = IrrigationScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global active_model
    logger.info("Initializing ML Serving Service...")
    active_model = load_active_model()
    logger.info(f"ML Serving Service ready. Active model: {active_model.model_name}")
    yield


app = FastAPI(
    title="Smart Irrigation AI Engine",
    description="Machine learning inference and optimization service for precision agricultural irrigation.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Liveness probe reporting model readiness and active model info."""
    return HealthResponse(
        status="healthy",
        service="ml-irrigation-serving",
        model_loaded=active_model is not None,
        active_model=active_model.model_name,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.get("/model/info", response_model=ModelInfoResponse)
def get_model_info():
    """Returns metadata, hyperparameter performance, and versioning for active model."""
    return ModelInfoResponse(
        active_model=active_model.model_name,
        version=active_model.version,
        metrics=active_model.metrics,
        trained_at=active_model.trained_at,
        artifact_path=active_model.artifact_path,
    )


@app.post("/predict/irrigation", response_model=IrrigationPredictResponse)
def predict_irrigation(request: IrrigationPredictRequest):
    """Predict whether irrigation is required based on field conditions."""
    feat_dict = request.model_dump()
    req, vol, conf, _ = active_model.predict_features(feat_dict)
    return IrrigationPredictResponse(
        irrigation_required=req,
        confidence_score=conf,
        model_name=active_model.model_name,
        model_version=active_model.version,
    )


@app.post("/predict/volume", response_model=VolumePredictResponse)
def predict_volume(request: IrrigationPredictRequest):
    """Predict recommended irrigation water delivery volume in Liters."""
    feat_dict = request.model_dump()
    _, vol, conf, _ = active_model.predict_features(feat_dict)
    return VolumePredictResponse(
        predicted_volume_liters=vol,
        confidence_score=conf,
        model_name=active_model.model_name,
        model_version=active_model.version,
    )


@app.post("/predict/schedule", response_model=ScheduleResponse)
def predict_schedule(request: IrrigationPredictRequest):
    """Generate comprehensive scheduled irrigation recommendation."""
    feat_dict = request.model_dump()
    req, vol, conf, rec_hour = active_model.predict_features(feat_dict)

    prediction_result = {
        "irrigation_required": req,
        "predicted_volume_liters": vol,
        "confidence_score": conf,
        "recommended_hour": rec_hour,
        "model_name": active_model.model_name,
        "model_version": active_model.version,
    }

    schedule_plan = scheduler.generate_schedule(
        field_id=request.field_id or 1,
        prediction_result=prediction_result,
        context=feat_dict,
        db=None,
    )
    return ScheduleResponse(**schedule_plan)


@app.get("/predict/field/{field_id}", response_model=ScheduleResponse, tags=["Field Inference"])
@app.post("/predict/field/{field_id}", response_model=ScheduleResponse, tags=["Field Inference"])
def predict_for_field(field_id: int, db: Session = Depends(get_db)):
    """
    End-to-end endpoint: Fetches DB context for field_id, executes prediction,
    runs optimal scheduler, and optionally persists the schedule.
    """
    if not active_model:
        raise HTTPException(status_code=503, detail="Model engine not initialized.")

    # 1. Fetch Field
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail=f"Field {field_id} not found.")

    # 2. Fetch Active Crop
    crop = db.query(Crop).filter(Crop.field_id == field_id, Crop.is_active == True).first()
    crop_type = crop.crop_type if crop else "Tomato"
    growth_stage = crop.growth_stage if crop else "Vegetative"
    kc_factor = float(cast(Any, crop.kc_factor)) if crop else 1.0

    # 3. Fetch Latest Sensor Reading
    reading = (
        db.query(SensorReading)
        .filter(SensorReading.field_id == field_id, SensorReading.is_valid == True)
        .order_by(SensorReading.timestamp.desc())
        .first()
    )
    soil_moisture = float(cast(Any, reading.soil_moisture)) if reading else 26.0

    # 4. Fetch Latest Weather Data
    weather = (
        db.query(WeatherData)
        .filter(WeatherData.field_id == field_id)
        .order_by(WeatherData.timestamp.desc())
        .first()
    )
    temp = float(cast(Any, weather.temperature)) if weather else 27.5
    humidity = float(cast(Any, weather.humidity)) if weather else 55.0
    rain_prob = float(cast(Any, weather.rain_probability)) if weather else 12.0
    rainfall_1h = float(cast(Any, weather.rainfall_1h)) if weather else 0.0
    solar_rad = float(cast(Any, weather.solar_radiation)) if weather and weather.solar_radiation is not None else 650.0

    feat_dict = {
        "field_id": field_id,
        "soil_moisture": soil_moisture,
        "temperature": temp,
        "humidity": humidity,
        "rainfall_1h": rainfall_1h,
        "rainfall_24h": 0.0,
        "rain_probability": rain_prob,
        "solar_radiation": solar_rad,
        "soil_type": str(field.soil_type),
        "crop_type": crop_type,
        "growth_stage": growth_stage,
        "kc_factor": kc_factor,
        "size_hectares": float(cast(Any, field.size_hectares)),
        "hour_of_day": datetime.now(timezone.utc).hour,
    }

    # 5. Run ML inference
    req, vol, conf, rec_hour = active_model.predict_features(feat_dict)

    prediction_result = {
        "irrigation_required": req,
        "predicted_volume_liters": vol,
        "confidence_score": conf,
        "recommended_hour": rec_hour,
        "model_name": active_model.model_name,
        "model_version": active_model.version,
    }

    # 6. Generate Schedule and persist to DB
    schedule_plan = scheduler.generate_schedule(
        field_id=field_id,
        prediction_result=prediction_result,
        context=feat_dict,
        db=db,
    )

    return ScheduleResponse(**schedule_plan)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
