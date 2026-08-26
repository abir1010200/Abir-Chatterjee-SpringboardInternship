from fastapi import APIRouter
from backend.app.api.v1.endpoints import sensors, health, weather

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["System Health"])
api_router.include_router(sensors.router, prefix="/sensors", tags=["Sensor Telemetry Ingestion"])
api_router.include_router(weather.router, prefix="/weather", tags=["Meteorological & Weather Services"])
