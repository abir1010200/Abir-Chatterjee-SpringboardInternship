from fastapi import APIRouter
from backend.app.api.v1.endpoints import sensors, health, weather, fields, cleaning, ml, notifications, reports, auth

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Farmer Authentication & Session"])
api_router.include_router(health.router, prefix="/health", tags=["System Health"])
api_router.include_router(sensors.router, prefix="/sensors", tags=["Sensor Telemetry Ingestion"])
api_router.include_router(weather.router, prefix="/weather", tags=["Meteorological & Weather Services"])
api_router.include_router(fields.router, prefix="/fields", tags=["Farmer, Field & Crop Configuration"])
api_router.include_router(cleaning.router, prefix="/cleaning", tags=["Data Cleaning & ML Feature Pipeline"])
api_router.include_router(ml.router, prefix="/ml", tags=["ML Irrigation Intelligence Engine"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Alerts & Notifications"])
api_router.include_router(reports.router, prefix="/reports", tags=["CSV & PDF Reports"])

