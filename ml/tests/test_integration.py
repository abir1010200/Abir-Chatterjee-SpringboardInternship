"""
ml/tests/test_integration.py
End-to-end integration tests for data pipeline, model training,
schedule optimization, and database persistence.
"""
import sys
import tempfile
from pathlib import Path
from datetime import datetime, timezone
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from backend.app.db.session import SessionLocal, Base, engine
from backend.app.models.field import Field
from backend.app.models.crop import Crop
from backend.app.models.farmer import Farmer
from ml.data.synthetic_generator import generate_synthetic_dataset
from ml.features.engineering import engineer_features
from ml.preprocessing.pipeline import build_preprocessing_pipeline, ALL_FEATURES
from ml.models.random_forest import RandomForestIrrigationModel
from ml.optimization.scheduler import IrrigationScheduler
from ml.db.models import MLModelRegistry, IrrigationPrediction, IrrigationSchedule


@pytest.fixture(scope="module")
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Create test farmer, field, and crop if missing
    farmer = db.query(Farmer).first()
    if not farmer:
        farmer = Farmer(name="Integration Farmer", email="test@farm.io", phone="1234567890")
        db.add(farmer)
        db.flush()

    field = db.query(Field).first()
    if not field:
        field = Field(farmer_id=farmer.id, name="Test Field 1", latitude=19.0, longitude=73.0, size_hectares=2.5, soil_type="Loam")
        db.add(field)
        db.flush()

    crop = db.query(Crop).filter(Crop.field_id == field.id, Crop.is_active == True).first()
    if not crop:
        crop = Crop(field_id=field.id, crop_type="Tomato", growth_stage="Flowering", kc_factor=1.1, is_active=True)
        db.add(crop)
        db.flush()

    db.commit()
    yield db, field.id
    db.close()


def test_end_to_end_ml_cycle(setup_test_db):
    db, field_id = setup_test_db

    # 1. Generate synthetic data
    raw_df = generate_synthetic_dataset(field_id=field_id, days=10, interval_hours=1)
    assert len(raw_df) > 50

    # 2. Engineer features
    feat_df = engineer_features(raw_df)
    assert "moisture_deficit" in feat_df.columns
    assert "sm_x_temp" in feat_df.columns

    # 3. Fit pipeline & model
    pipe = build_preprocessing_pipeline()
    X = pipe.fit_transform(feat_df)
    y_cls = feat_df["irrigation_required"].values.astype(int)
    y_vol = feat_df["irrigation_volume_liters"].values.astype(float)

    rf = RandomForestIrrigationModel(n_estimators=10, max_depth=4)
    rf.fit(X, y_cls, y_vol=y_vol, feature_names=ALL_FEATURES)

    # 4. Predict
    pred_cls, pred_vol, conf = rf.predict(X[:1])
    assert len(pred_cls) == 1
    assert 0.0 <= conf[0] <= 1.0

    # 5. Optimize schedule & persist to DB
    scheduler = IrrigationScheduler()
    pred_dict = {
        "irrigation_required": bool(pred_cls[0]),
        "predicted_volume_liters": float(pred_vol[0]),
        "confidence_score": float(conf[0]),
        "recommended_hour": 6,
        "model_name": rf.name,
        "model_version": rf.version,
    }
    context = {
        "soil_moisture": float(feat_df["soil_moisture"].iloc[0]),
        "soil_type": "Loam",
        "rain_probability": 10.0,
        "temperature": 29.0,
        "crop_type": "Tomato",
        "growth_stage": "Flowering",
    }

    schedule_plan = scheduler.generate_schedule(
        field_id=field_id,
        prediction_result=pred_dict,
        context=context,
        db=db,
    )

    assert "prediction_id" in schedule_plan
    assert schedule_plan["priority"] in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    assert "agronomic_context" in schedule_plan

    # Verify stored in DB
    db_pred = db.query(IrrigationPrediction).filter(IrrigationPrediction.id == schedule_plan["prediction_id"]).first()
    assert db_pred is not None
    assert db_pred.field_id == field_id
