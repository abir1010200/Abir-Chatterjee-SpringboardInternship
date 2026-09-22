import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # API & Core
    PROJECT_NAME: str = "KrishiPals — AI Smart Irrigation Ecosystem"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "*"]

    # Database
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "smart_irrigation"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: Optional[str] = None

    # MQTT Broker
    MQTT_BROKER_HOST: str = "localhost"
    MQTT_BROKER_PORT: int = 1883
    MQTT_TOPIC_PREFIX: str = "farm/+/field/+/sensor/+/reading"
    MQTT_CLIENT_ID: str = "smart_irrigation_subscriber"

    # Weather API
    OPENWEATHER_API_KEY: str = ""
    TOMORROW_API_KEY: str = ""
    WEATHER_POLL_INTERVAL_MINUTES: int = 30
    WEATHER_CACHE_TTL_MINUTES: int = 60

    # Sensor Telemetry Thresholds
    SENSOR_STALE_THRESHOLD_MINUTES: int = 15
    SENSOR_OFFLINE_THRESHOLD_MINUTES: int = 60
    MIN_SOIL_MOISTURE: float = 0.0
    MAX_SOIL_MOISTURE: float = 100.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )

    def get_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()
