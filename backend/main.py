import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.db.init_db import init_db, seed_db
from backend.app.api.v1.api import api_router
from backend.app.services.mqtt_subscriber import mqtt_service
from backend.app.services.weather.scheduler import weather_scheduler

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("smart_irrigation_app")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup:
    logger.info("Starting AI-Powered Smart Irrigation Ingestion Engine...")
    init_db()
    seed_db()
    mqtt_service.start()
    weather_scheduler.start()
    yield
    # Shutdown:
    logger.info("Shutting down background services...")
    weather_scheduler.stop()
    mqtt_service.stop()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Data Ingestion, Weather Integration, and Soil Moisture Telemetry Engine (Milestone 1)",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
