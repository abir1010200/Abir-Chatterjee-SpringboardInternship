from fastapi import APIRouter
from backend.app.api.v1.endpoints import sensors, health, weather, fields

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["System Health"])
api_router.include_router(sensors.router, prefix="/sensors", tags=["Sensor Telemetry Ingestion"])
api_router.include_router(weather.router, prefix="/weather", tags=["Meteorological & Weather Services"])
api_router.include_router(fields.router, prefix="/fields", tags=["Farmer, Field & Crop Configuration"])
