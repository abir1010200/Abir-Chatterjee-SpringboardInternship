from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, ConfigDict

# --- Farmer Schemas ---
class FarmerBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=30)
    address: Optional[str] = Field(None, max_length=255)

class FarmerCreate(FarmerBase):
    pass

class FarmerResponse(FarmerBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# --- Crop Schemas ---
class CropBase(BaseModel):
    crop_type: str = Field(..., min_length=2, max_length=50, description="e.g. Wheat, Tomato, Maize, Rice")
    growth_stage: str = Field("Initial", description="Initial, Vegetative, Flowering, Mid-Season, Late-Season, Harvest")
    planted_date: date = Field(default_factory=date.today)
    expected_harvest_date: Optional[date] = None
    kc_factor: float = Field(1.0, ge=0.2, le=2.0, description="Crop water requirement coefficient Kc")
    is_active: bool = True

class CropCreate(CropBase):
    field_id: int

class CropUpdate(BaseModel):
    growth_stage: Optional[str] = None
    kc_factor: Optional[float] = None
    expected_harvest_date: Optional[date] = None
    is_active: Optional[bool] = None

class CropResponse(CropBase):
    id: int
    field_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# --- Sensor Config Schema ---
class SensorCreate(BaseModel):
    sensor_id: str = Field(..., min_length=2, max_length=50)
    sensor_type: str = "soil_moisture"
    model_name: Optional[str] = "Capacitive-FDR-v2"

class SensorResponse(BaseModel):
    id: str
    field_id: int
    sensor_type: str
    model_name: Optional[str]
    status: str
    battery_level: Optional[float]
    last_seen: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)

# --- Field Schemas ---
class FieldBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    size_hectares: float = Field(..., gt=0.0)
    soil_type: str = Field("Loam", description="Clay, Sandy Loam, Silty Clay, Peat, Loam")

class FieldCreate(FieldBase):
    farmer_id: int

class FieldResponse(FieldBase):
    id: int
    farmer_id: int
    created_at: datetime
    crops: List[CropResponse] = []
    sensors: List[SensorResponse] = []
    model_config = ConfigDict(from_attributes=True)

# --- Composite Registration Payload (Farmer + Field + Crop + Sensor) ---
class CompositeFieldRegistration(BaseModel):
    farmer: FarmerCreate
    field: FieldBase
    crop: CropBase
    sensor: SensorCreate
