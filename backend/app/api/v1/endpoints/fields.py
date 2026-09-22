import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.farmer import Farmer
from backend.app.models.field import Field
from backend.app.models.crop import Crop
from backend.app.models.sensor import Sensor
from backend.app.models.irrigation_history import IrrigationHistory
from backend.app.schemas.field_config import (
    FarmerCreate,
    FarmerUpdate,
    FarmerResponse,
    FieldCreate,
    FieldResponse,
    CropCreate,
    CropUpdate,
    CropResponse,
    CompositeFieldRegistration,
    IrrigationHistoryCreate,
    IrrigationHistoryResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()

# --- Composite Field Registration ---
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_composite_field(
    payload: CompositeFieldRegistration,
    db: Session = Depends(get_db)
):
    """
    Composite Atomic Registration Endpoint:
    Captures Farmer profile, creates Field, assigns active Crop with Kc coefficient,
    and binds the initial IoT Soil Moisture Sensor ID.
    Enforces relational integrity in a single database transaction.
    """
    try:
        # 1. Farmer (lookup existing by email or create new)
        farmer = db.query(Farmer).filter(Farmer.email == payload.farmer.email).first()
        if not farmer:
            farmer = Farmer(
                name=payload.farmer.name,
                email=payload.farmer.email,
                phone=payload.farmer.phone,
                address=payload.farmer.address
            )
            db.add(farmer)
            db.flush()

        # 2. Field
        field = Field(
            farmer_id=farmer.id,
            name=payload.field.name,
            latitude=payload.field.latitude,
            longitude=payload.field.longitude,
            size_hectares=payload.field.size_hectares,
            soil_type=payload.field.soil_type
        )
        db.add(field)
        db.flush()

        # 3. Crop
        crop = Crop(
            field_id=field.id,
            crop_type=payload.crop.crop_type,
            growth_stage=payload.crop.growth_stage,
            planted_date=payload.crop.planted_date,
            expected_harvest_date=payload.crop.expected_harvest_date,
            kc_factor=payload.crop.kc_factor,
            is_active=True
        )
        db.add(crop)

        # 4. Sensor
        sensor = db.query(Sensor).filter(Sensor.id == payload.sensor.sensor_id).first()
        if sensor:
            setattr(sensor, "field_id", field.id)
            setattr(sensor, "sensor_type", payload.sensor.sensor_type)
        else:
            sensor = Sensor(
                id=payload.sensor.sensor_id,
                field_id=field.id,
                sensor_type=payload.sensor.sensor_type,
                model_name=payload.sensor.model_name,
                status="active"
            )
            db.add(sensor)

        db.commit()
        db.refresh(field)

        logger.info(
            f"Registered composite field id={field.id} ('{field.name}') for Farmer '{farmer.name}' "
            f"with Crop '{crop.crop_type}' and Sensor '{sensor.id}'"
        )

        return {
            "status": "success",
            "message": "Field, Farmer, Crop, and Sensor successfully registered",
            "farmer_id": farmer.id,
            "field_id": field.id,
            "crop_id": crop.id,
            "sensor_id": sensor.id
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to register composite field: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Registration failed: {str(e)}")

# --- Field CRUD ---
@router.get("/", response_model=List[FieldResponse])
def list_fields(db: Session = Depends(get_db)):
    """List all registered fields with active crops and sensors."""
    return db.query(Field).all()

@router.get("/{field_id}", response_model=FieldResponse)
def get_field(field_id: int, db: Session = Depends(get_db)):
    """Retrieve detailed field configuration."""
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Field not found")
    return field

@router.post("/", response_model=FieldResponse, status_code=status.HTTP_201_CREATED)
def create_field(payload: FieldCreate, db: Session = Depends(get_db)):
    """Create a new field under an existing farmer."""
    farmer = db.query(Farmer).filter(Farmer.id == payload.farmer_id).first()
    if not farmer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farmer not found")

    field = Field(
        farmer_id=payload.farmer_id,
        name=payload.name,
        latitude=payload.latitude,
        longitude=payload.longitude,
        size_hectares=payload.size_hectares,
        soil_type=payload.soil_type
    )
    db.add(field)
    db.commit()
    db.refresh(field)
    return field

@router.delete("/{field_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_field(field_id: int, db: Session = Depends(get_db)):
    """Delete a field and cascade delete associated crops, sensors, and readings."""
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Field not found")
    db.delete(field)
    db.commit()
    return None

# --- Farmer Endpoints ---
@router.get("/farmers/all", response_model=List[FarmerResponse])
def list_farmers(db: Session = Depends(get_db)):
    """List all registered farmers."""
    return db.query(Farmer).all()

@router.post("/farmers", response_model=FarmerResponse, status_code=status.HTTP_201_CREATED)
def create_farmer(payload: FarmerCreate, db: Session = Depends(get_db)):
    """Register a new farmer profile."""
    existing = db.query(Farmer).filter(Farmer.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    farmer = Farmer(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        address=payload.address
    )
    db.add(farmer)
    db.commit()
    db.refresh(farmer)
    return farmer

# --- Crop Endpoints ---
@router.post("/crops", response_model=CropResponse, status_code=status.HTTP_201_CREATED)
def create_crop(payload: CropCreate, db: Session = Depends(get_db)):
    """Register a new crop cycle for a field."""
    field = db.query(Field).filter(Field.id == payload.field_id).first()
    if not field:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Field not found")

    crop = Crop(
        field_id=payload.field_id,
        crop_type=payload.crop_type,
        growth_stage=payload.growth_stage,
        planted_date=payload.planted_date,
        expected_harvest_date=payload.expected_harvest_date,
        kc_factor=payload.kc_factor,
        is_active=payload.is_active
    )
    db.add(crop)
    db.commit()
    db.refresh(crop)
    return crop

@router.put("/crops/{crop_id}", response_model=CropResponse)
def update_crop_stage(crop_id: int, payload: CropUpdate, db: Session = Depends(get_db)):
    """Update crop growth stage or Kc water coefficient."""
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crop not found")

    if payload.growth_stage is not None:
        setattr(crop, "growth_stage", payload.growth_stage)
    if payload.kc_factor is not None:
        setattr(crop, "kc_factor", payload.kc_factor)
    if payload.expected_harvest_date is not None:
        setattr(crop, "expected_harvest_date", payload.expected_harvest_date)
    if payload.is_active is not None:
        setattr(crop, "is_active", payload.is_active)

    db.commit()
    db.refresh(crop)
    return crop

@router.put("/farmers/{farmer_id}", response_model=FarmerResponse)
def update_farmer(farmer_id: int, payload: FarmerUpdate, db: Session = Depends(get_db)):
    """Update farmer profile parameters (Name, Phone, Email, Address)."""
    farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    if not farmer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farmer profile not found")

    if payload.name is not None:
        setattr(farmer, "name", payload.name)
    if payload.email is not None:
        setattr(farmer, "email", payload.email)
    if payload.phone is not None:
        setattr(farmer, "phone", payload.phone)
    if payload.address is not None:
        setattr(farmer, "address", payload.address)

    db.commit()
    db.refresh(farmer)
    return farmer

# --- Irrigation History Endpoints ---
@router.post("/irrigation/history", response_model=IrrigationHistoryResponse, status_code=status.HTTP_201_CREATED)
def record_irrigation_event(payload: IrrigationHistoryCreate, db: Session = Depends(get_db)):
    """Record an irrigation event (manual log or automated dispatch)."""
    field = db.query(Field).filter(Field.id == payload.field_id).first()
    if not field:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Field not found")

    history = IrrigationHistory(
        field_id=payload.field_id,
        volume_liters=payload.volume_liters,
        start_time=payload.start_time,
        end_time=payload.end_time,
        duration_minutes=payload.duration_minutes,
        trigger_source=payload.trigger_source,
        status=payload.status,
        notes=payload.notes,
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    return history

@router.get("/irrigation/history/field/{field_id}", response_model=List[IrrigationHistoryResponse])
def get_field_irrigation_history(field_id: int, db: Session = Depends(get_db)):
    """Retrieve historical irrigation records for a specific field."""
    records = (
        db.query(IrrigationHistory)
        .filter(IrrigationHistory.field_id == field_id)
        .order_by(IrrigationHistory.start_time.desc())
        .all()
    )
    return records

@router.get("/irrigation/history/all", response_model=List[IrrigationHistoryResponse])
def get_all_irrigation_history(db: Session = Depends(get_db)):
    """Retrieve all historical irrigation logs across fields."""
    return db.query(IrrigationHistory).order_by(IrrigationHistory.start_time.desc()).all()

