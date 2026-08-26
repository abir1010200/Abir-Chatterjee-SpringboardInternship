from fastapi import APIRouter
from backend.app.api.v1.endpoints import sensors, health

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["System Health"])
api_router.include_router(sensors.router, prefix="/sensors", tags=["Sensor Telemetry Ingestion"])
