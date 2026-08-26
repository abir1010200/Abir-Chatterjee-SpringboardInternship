import logging
from datetime import datetime, timezone
from typing import Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from backend.app.models.sensor import Sensor
from backend.app.models.field import Field
from backend.app.models.sensor_reading import SensorReading
from backend.app.schemas.sensor_reading import SensorReadingCreate

logger = logging.getLogger(__name__)

def ingest_sensor_reading(
    db: Session,
    payload: SensorReadingCreate,
    source: str = "rest"
) -> Tuple[SensorReading, bool]:
    """
    Unified ingestion engine shared across REST API endpoints and MQTT subscribers.
    
    Performs:
    1. Verification / Auto-registration of Sensor and Field association
    2. Heartbeat & status update on the Sensor entity
    3. Idempotent deduplication check on (sensor_id, timestamp)
    4. Durable storage into the time-series SensorReading table
    
    Returns:
        Tuple[SensorReading, bool]: (reading_object, is_duplicate)
    """
    # 1. Verify or ensure field exists
    field = db.query(Field).filter(Field.id == payload.field_id).first()
    if not field:
        logger.warning(f"Ingestion warning: Field ID {payload.field_id} does not exist. Sensor reading will still be saved.")

    # 2. Update or register Sensor hardware status
    sensor = db.query(Sensor).filter(Sensor.id == payload.sensor_id).first()
    if not sensor:
        logger.info(f"Auto-registering newly detected sensor: {payload.sensor_id} for Field {payload.field_id}")
        sensor = Sensor(
            id=payload.sensor_id,
            field_id=payload.field_id,
            sensor_type="soil_moisture",
            model_name="Auto-Detected-FDR",
            status="active",
            battery_level=payload.battery_level,
            last_seen=payload.timestamp
        )
        db.add(sensor)
    else:
        # Update heartbeat and battery
        sensor.status = "active"
        sensor.last_seen = payload.timestamp
        if payload.battery_level is not None:
            sensor.battery_level = payload.battery_level

    # 3. Idempotency Check: Check if duplicate (sensor_id, timestamp) already exists
    existing_reading = db.query(SensorReading).filter(
        SensorReading.sensor_id == payload.sensor_id,
        SensorReading.timestamp == payload.timestamp
    ).first()

    if existing_reading:
        logger.info(
            f"Duplicate reading detected from {source} for sensor={payload.sensor_id} at {payload.timestamp.isoformat()}. "
            f"Idempotently returning existing record ID {existing_reading.id}."
        )
        return existing_reading, True

    # 4. Create and persist new SensorReading
    new_reading = SensorReading(
        sensor_id=payload.sensor_id,
        field_id=payload.field_id,
        soil_moisture=payload.soil_moisture,
        temperature_soil=payload.temperature_soil,
        battery_level=payload.battery_level,
        timestamp=payload.timestamp,
        is_valid=True,
        cleaning_flag="raw"
    )

    try:
        db.add(new_reading)
        db.commit()
        db.refresh(new_reading)
        logger.info(
            f"Successfully ingested telemetry [{source}] id={new_reading.id} sensor={payload.sensor_id} "
            f"moisture={payload.soil_moisture}% field={payload.field_id}"
        )
        return new_reading, False
    except IntegrityError as ie:
        db.rollback()
        # Concurrency race condition duplicate check
        existing = db.query(SensorReading).filter(
            SensorReading.sensor_id == payload.sensor_id,
            SensorReading.timestamp == payload.timestamp
        ).first()
        if existing:
            return existing, True
        raise ie
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to ingest sensor reading for sensor={payload.sensor_id}: {e}")
        raise
