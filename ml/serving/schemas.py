"""
ml/serving/schemas.py
Pydantic v2 data transfer schemas for ML Serving API.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class IrrigationPredictRequest(BaseModel):
    """Features required for irrigation necessity inference."""
    soil_moisture: float = Field(..., ge=0.0, le=100.0, description="Current soil moisture percentage (0-100%)")
    temperature: float = Field(25.0, ge=-20.0, le=60.0, description="Ambient temperature (°C)")
    humidity: float = Field(60.0, ge=0.0, le=100.0, description="Relative humidity (%)")
    rainfall_1h: float = Field(0.0, ge=0.0, description="Rainfall in the past 1 hour (mm)")
    rainfall_24h: float = Field(0.0, ge=0.0, description="Rainfall in the past 24 hours (mm)")
    rain_probability: float = Field(10.0, ge=0.0, le=100.0, description="Precipitation probability forecast (%)")
    solar_radiation: float = Field(500.0, ge=0.0, description="Solar radiation (W/m²)")
    soil_type: str = Field("Loam", description="Soil texture type (Clay, Loam, Sandy, etc.)")
    crop_type: str = Field("Tomato", description="Cultivated crop name")
    growth_stage: str = Field("Vegetative", description="Crop phenological growth stage")
    kc_factor: float = Field(1.0, ge=0.1, le=2.0, description="FAO-56 Crop coefficient")
    size_hectares: float = Field(1.0, gt=0.0, description="Field surface area in hectares")
    hour_of_day: Optional[int] = Field(None, ge=0, le=23, description="Observation hour (0-23)")
    field_id: Optional[int] = Field(None, description="Optional field ID reference")


class IrrigationPredictResponse(BaseModel):
    """Inference output for classification."""
    irrigation_required: bool
    confidence_score: float
    model_name: str
    model_version: str


class VolumePredictResponse(BaseModel):
    """Inference output for volume regression."""
    predicted_volume_liters: float
    confidence_score: float
    model_name: str
    model_version: str


class ScheduleResponse(BaseModel):
    """Comprehensive actionable irrigation schedule output."""
    field_id: Optional[int] = None
    prediction_id: Optional[int] = None
    irrigation_required: bool
    confidence_score: float
    predicted_volume_liters: float
    recommended_duration_minutes: int
    recommended_start_time: Optional[str] = None
    priority: str
    risk_level: str
    reason: str
    agronomic_context: Dict[str, Any]
    model_metadata: Dict[str, Any]


class ModelInfoResponse(BaseModel):
    """Metadata describing the currently active served model."""
    active_model: str
    version: str
    metrics: Dict[str, Any]
    trained_at: Optional[str] = None
    artifact_path: Optional[str] = None


class HealthResponse(BaseModel):
    """Serving service liveness and readiness probe response."""
    status: str
    service: str
    model_loaded: bool
    active_model: str
    timestamp: str
