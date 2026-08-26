import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.field import Field
from backend.app.services.cleaning.pipeline import cleaning_pipeline

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/field/{field_id}/run")
def run_cleaning_job(
    field_id: int,
    db: Session = Depends(get_db)
):
    """
    Execute the data cleaning and validation pipeline for a specific field.
    Flags statistical outliers, evaluates gaps, and updates cleaning flags in the DB.
    """
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Field {field_id} not found")

    report = cleaning_pipeline.clean_sensor_readings(db=db, field_id=field_id)
    return report.to_dict()

@router.get("/field/{field_id}/ml-dataset")
def get_ml_prepared_dataset(
    field_id: int,
    limit: int = Query(200, ge=10, le=2000),
    db: Session = Depends(get_db)
):
    """
    Export cleaned, timestamp-aligned, multi-modal feature matrix
    (Sensor Soil Moisture + Soil Temp + Air Temp + Humidity + Rain Prob + Crop Kc + Deficit Target)
    specifically formatted for Milestone 2 Machine Learning (Random Forest & LSTM).
    """
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Field {field_id} not found")

    dataset = cleaning_pipeline.generate_ml_feature_dataset(db=db, field_id=field_id, limit=limit)
    return {
        "field_id": field_id,
        "field_name": field.name,
        "total_samples": len(dataset),
        "target_model_compatibility": ["RandomForestRegressor", "LSTMTimeSeriesPredictor"],
        "features": [
            "soil_moisture", "temperature_soil", "air_temperature", "humidity",
            "rainfall_1h", "rain_probability", "solar_radiation", "kc_factor"
        ],
        "target_variables": ["moisture_deficit", "irrigation_recommended"],
        "data": dataset
    }
