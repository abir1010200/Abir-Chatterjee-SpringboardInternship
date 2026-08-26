from datetime import datetime, timezone, timedelta
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict

class SensorReadingBase(BaseModel):
    sensor_id: str = Field(..., min_length=2, max_length=50, description="Unique sensor hardware identifier (e.g. SEN-WHEAT-01)")
    field_id: int = Field(..., gt=0, description="Target field ID")
    soil_moisture: float = Field(..., description="Soil volumetric moisture content percentage (0.0 - 100.0%)")
    temperature_soil: Optional[float] = Field(None, description="Soil temperature in degrees Celsius")
    battery_level: Optional[float] = Field(None, description="Sensor battery percentage (0.0 - 100.0%)")
    timestamp: datetime = Field(..., description="UTC ISO-8601 Timestamp of reading")

    @field_validator("soil_moisture")
    @classmethod
    def validate_soil_moisture(cls, v: float) -> float:
        if v < 0.0 or v > 100.0:
            raise ValueError(f"Soil moisture must be between 0.0% and 100.0%, received: {v}")
        return round(v, 2)

    @field_validator("battery_level")
    @classmethod
    def validate_battery_level(cls, v: Optional[float]) -> Optional[float]:
        if v is not None:
            if v < 0.0 or v > 100.0:
                raise ValueError(f"Battery level must be between 0.0% and 100.0%, received: {v}")
            return round(v, 1)
        return v

    @field_validator("temperature_soil")
    @classmethod
    def validate_temperature_soil(cls, v: Optional[float]) -> Optional[float]:
        if v is not None:
            if v < -20.0 or v > 70.0:
                raise ValueError(f"Soil temperature out of physical bounds (-20°C to 70°C), received: {v}")
            return round(v, 2)
        return v

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp_sanity(cls, v: datetime) -> datetime:
        # Ensure timezone-aware UTC
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        
        now = datetime.now(timezone.utc)
        # Prevent timestamps in the far future (allow 10-minute clock drift)
        if v > now + timedelta(minutes=10):
            raise ValueError(f"Timestamp cannot be in the future: {v.isoformat()} > {now.isoformat()}")
        # Prevent timestamps older than 2 years
        if v < now - timedelta(days=730):
            raise ValueError(f"Timestamp is too old (exceeds 2-year retention limit): {v.isoformat()}")
        return v

class SensorReadingCreate(SensorReadingBase):
    pass

class SensorReadingBatchCreate(BaseModel):
    readings: List[SensorReadingCreate] = Field(..., min_length=1, max_length=1000)

class SensorReadingResponse(SensorReadingBase):
    id: int
    is_valid: bool
    cleaning_flag: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class IngestionResult(BaseModel):
    status: str
    message: str
    reading_id: Optional[int] = None
    sensor_id: str
    is_duplicate: bool = False
    timestamp: datetime
