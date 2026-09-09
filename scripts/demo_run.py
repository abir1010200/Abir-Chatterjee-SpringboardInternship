import sys
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.db.init_db import init_db, seed_db
from backend.app.db.session import SessionLocal
from backend.app.models import Field, Crop, SensorReading, WeatherData
from ml.serving.model_loader import load_active_model
from ml.optimization.scheduler import IrrigationScheduler


def run_demo():
    print("=" * 70)
    print("AI SMART IRRIGATION SYSTEM -- MILESTONE 2 LIVE DEMONSTRATION")
    print("=" * 70)

    # 1. Init & Seed DB
    print("\n[STEP 1] Initializing & Seeding Database...")
    init_db()
    seed_db()

    db = SessionLocal()
    try:
        # 2. Query Active Field & Telemetry
        print("\n[STEP 2] Fetching Field Telemetry from Database (Field ID: 1)...")
        field = db.query(Field).filter(Field.id == 1).first()
        crop = db.query(Crop).filter(Crop.field_id == 1, Crop.is_active == True).first()
        reading = db.query(SensorReading).filter(SensorReading.field_id == 1).order_by(SensorReading.timestamp.desc()).first()
        weather = db.query(WeatherData).filter(WeatherData.field_id == 1).order_by(WeatherData.timestamp.desc()).first()

        print(f"  - Field Name      : {field.name if field else 'North Valley Wheat'}")
        print(f"  - Soil Type       : {field.soil_type if field else 'Clay Loam'}")
        print(f"  - Crop Type       : {crop.crop_type if crop else 'Wheat'}")
        print(f"  - Growth Stage    : {crop.growth_stage if crop else 'Vegetative'} (Kc = {crop.kc_factor if crop else 1.15})")
        print(f"  - Soil Moisture   : {reading.soil_moisture if reading else 24.5}%")
        print(f"  - Air Temp        : {weather.temperature if weather else 28.0}C | Humidity: {weather.humidity if weather else 45.0}%")
        print(f"  - Rain Forecast   : {weather.rain_probability if weather else 10.0}% probability")

        # 3. Load Active ML Model
        print("\n[STEP 3] Loading Active Champion Model...")
        model = load_active_model()
        print(f"  - Active Model    : {model.model_name}")
        print(f"  - Version         : {model.version}")
        print(f"  - Metrics         : {json.dumps(model.metrics)}")

        # 4. Feature Vector & Model Inference
        feat_dict = {
            "field_id": 1,
            "soil_moisture": float(reading.soil_moisture) if reading else 24.5,
            "temperature": float(weather.temperature) if weather else 28.0,
            "humidity": float(weather.humidity) if weather else 45.0,
            "rainfall_1h": 0.0,
            "rainfall_24h": 0.0,
            "rain_probability": float(weather.rain_probability) if weather else 10.0,
            "solar_radiation": 650.0,
            "soil_type": str(field.soil_type) if field else "Clay Loam",
            "crop_type": crop.crop_type if crop else "Wheat",
            "growth_stage": crop.growth_stage if crop else "Vegetative",
            "kc_factor": float(crop.kc_factor) if crop else 1.15,
            "size_hectares": float(field.size_hectares) if field else 4.5,
            "hour_of_day": datetime.now(timezone.utc).hour,
        }

        print("\n[STEP 4] Running ML Model Inference...")
        req, vol, conf, rec_hour = model.predict_features(feat_dict)
        print(f"  - Irrigation Required : {req}")
        print(f"  - Predicted Volume    : {vol:,.2f} Liters")
        print(f"  - Confidence Score    : {conf * 100:.1f}%")

        # 5. Optimization Scheduler
        print("\n[STEP 5] Generating Actionable Field Schedule...")
        scheduler = IrrigationScheduler()
        prediction_result = {
            "irrigation_required": req,
            "predicted_volume_liters": vol,
            "confidence_score": conf,
            "recommended_hour": rec_hour,
            "model_name": model.model_name,
            "model_version": model.version,
        }
        schedule = scheduler.generate_schedule(field_id=1, prediction_result=prediction_result, context=feat_dict, db=db)

        print("\n" + "=" * 70)
        print("ACTIONABLE ML IRRIGATION SCHEDULE OUTPUT (JSON)")
        print("=" * 70)
        print(json.dumps(schedule, indent=2))
        print("=" * 70)
    finally:
        db.close()


if __name__ == "__main__":
    run_demo()
