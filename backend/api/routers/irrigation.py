"""
backend/api/routers/irrigation.py
FastAPI Router for ML Irrigation Prediction & Scheduling.
Extends FastAPI routes for ML inference, volume prediction, and schedule persistence.
"""
from fastapi import APIRouter
from backend.app.api.v1.endpoints.ml import (
    router as ml_router,
    get_ml_health,
    get_model_info,
    predict_irrigation,
    predict_volume,
    predict_schedule,
    get_field_recommendation,
)

router = APIRouter(prefix="/irrigation", tags=["ML Irrigation Scheduling Engine"])
router.include_router(ml_router)
