import logging
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.field import Field
from backend.app.services.weather.service import weather_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/field/{field_id}/latest")
async def get_latest_weather(
    field_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve the most recent meteorological observation for a specific field.
    If no observation exists, automatically fetches and stores one.
    """
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Field with ID {field_id} not found")

    record = weather_service.get_latest_weather(db=db, field_id=field_id)
    if not record:
        record = await weather_service.fetch_weather_for_field(db=db, field=field)

    return {
        "id": record.id,
        "field_id": record.field_id,
        "temperature": record.temperature,
        "humidity": record.humidity,
        "rainfall_1h": record.rainfall_1h,
        "rainfall_24h": record.rainfall_24h,
        "rain_probability": record.rain_probability,
        "wind_speed": record.wind_speed,
        "solar_radiation": record.solar_radiation,
        "forecast_json": record.forecast_json,
        "provider": record.provider,
        "timestamp": record.timestamp.isoformat()
    }

@router.get("/field/{field_id}/history")
def get_weather_history(
    field_id: int,
    limit: int = Query(100, ge=1, le=1000),
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve historical weather time-series records for a specific field.
    """
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Field with ID {field_id} not found")

    records = weather_service.get_weather_history(
        db=db,
        field_id=field_id,
        limit=limit,
        start_time=start_time,
        end_time=end_time
    )

    return [
        {
            "id": r.id,
            "field_id": r.field_id,
            "temperature": r.temperature,
            "humidity": r.humidity,
            "rainfall_1h": r.rainfall_1h,
            "rainfall_24h": r.rainfall_24h,
            "rain_probability": r.rain_probability,
            "wind_speed": r.wind_speed,
            "solar_radiation": r.solar_radiation,
            "provider": r.provider,
            "timestamp": r.timestamp.isoformat()
        }
        for r in records
    ]

@router.post("/field/{field_id}/sync")
async def sync_weather_now(
    field_id: int,
    db: Session = Depends(get_db)
):
    """
    Force an immediate live meteorological sync for a field from the weather provider.
    """
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Field with ID {field_id} not found")

    record = await weather_service.fetch_weather_for_field(db=db, field=field, force_refresh=True)

    return {
        "status": "success",
        "message": f"Synchronized weather for Field {field.name} ({field_id})",
        "weather_record_id": record.id,
        "temperature": record.temperature,
        "humidity": record.humidity,
        "rain_probability": record.rain_probability,
        "rainfall_1h": record.rainfall_1h,
        "provider": record.provider,
        "timestamp": record.timestamp.isoformat()
    }
