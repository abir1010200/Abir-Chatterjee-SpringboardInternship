import logging
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.sensor import Sensor
from backend.app.models.sensor_reading import SensorReading
from backend.app.schemas.sensor_reading import (
    SensorReadingCreate,
    SensorReadingBatchCreate,
    SensorReadingResponse,
    IngestionResult,
)
from backend.app.services.ingestion import ingest_sensor_reading

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/readings", response_model=IngestionResult, status_code=status.HTTP_201_CREATED)
def create_sensor_reading(
    payload: SensorReadingCreate,
    db: Session = Depends(get_db)
):
    """
    Ingest a single soil moisture sensor reading via REST API.
    Validates physical boundaries, ensures timestamp sanity, and provides idempotent deduplication.
    """
    try:
        reading, is_duplicate = ingest_sensor_reading(db=db, payload=payload, source="rest")
        return IngestionResult(
            status="duplicate" if is_duplicate else "success",
            message="Duplicate reading acknowledged" if is_duplicate else "Reading successfully ingested",
            reading_id=reading.id,
            sensor_id=reading.sensor_id,
            is_duplicate=is_duplicate,
            timestamp=reading.timestamp
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))
    except Exception as e:
        logger.error(f"Error processing sensor reading: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to store sensor reading")

@router.post("/readings/batch", response_model=List[IngestionResult], status_code=status.HTTP_201_CREATED)
def create_sensor_readings_batch(
    payload: SensorReadingBatchCreate,
    db: Session = Depends(get_db)
):
    """
    Batch ingestion endpoint for buffered or offline sensor gateways.
    Processes up to 1,000 readings per transaction.
    """
    results = []
    for item in payload.readings:
        try:
            reading, is_dup = ingest_sensor_reading(db=db, payload=item, source="rest_batch")
            results.append(
                IngestionResult(
                    status="duplicate" if is_dup else "success",
                    message="Duplicate acknowledged" if is_dup else "Ingested",
                    reading_id=reading.id,
                    sensor_id=reading.sensor_id,
                    is_duplicate=is_dup,
                    timestamp=reading.timestamp
                )
            )
        except Exception as e:
            logger.error(f"Batch item failed for {item.sensor_id}: {e}")
            results.append(
                IngestionResult(
                    status="error",
                    message=str(e),
                    sensor_id=item.sensor_id,
                    is_duplicate=False,
                    timestamp=item.timestamp
                )
            )
    return results

@router.get("/{sensor_id}/readings", response_model=List[SensorReadingResponse])
def get_sensor_readings(
    sensor_id: str,
    limit: int = Query(100, ge=1, le=1000),
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """
    Query historical time-series readings for a given sensor ID.
    Leverages indexed (sensor_id, timestamp) for rapid query performance.
    """
    query = db.query(SensorReading).filter(SensorReading.sensor_id == sensor_id)
    if start_time:
        query = query.filter(SensorReading.timestamp >= start_time)
    if end_time:
        query = query.filter(SensorReading.timestamp <= end_time)
    
    readings = query.order_by(SensorReading.timestamp.desc()).limit(limit).all()
    return readings

@router.get("/", response_model=List[dict])
def list_sensors(db: Session = Depends(get_db)):
    """
    List all registered sensors and their current status, battery level, and last heartbeat.
    """
    sensors = db.query(Sensor).all()
    return [
        {
            "id": s.id,
            "field_id": s.field_id,
            "sensor_type": s.sensor_type,
            "model_name": s.model_name,
            "status": s.status,
            "battery_level": s.battery_level,
            "last_seen": s.last_seen.isoformat() if s.last_seen else None,
            "install_date": s.install_date.isoformat() if s.install_date else None,
        }
        for s in sensors
    ]
