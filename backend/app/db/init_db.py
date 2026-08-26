import logging
from datetime import datetime, date, timezone, timedelta
from sqlalchemy import text
from backend.app.db.session import engine, SessionLocal, Base
from backend.app.models import Farmer, Field, Crop, Sensor, SensorReading, WeatherData, IrrigationHistory

logger = logging.getLogger(__name__)

def init_db():
    """Create all database tables defined in SQLAlchemy models."""
    logger.info("Initializing database schema...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema initialized successfully.")

def seed_db():
    """Seed initial demo data for testing."""
    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(Farmer).first():
            logger.info("Database already seeded. Skipping initial data insertion.")
            return

        logger.info("Seeding demo data...")
        # 1. Create Demo Farmer
        farmer = Farmer(
            name="Rajesh Patel",
            email="rajesh.patel@agrofarm.io",
            phone="+91-98765-43210",
            address="Plot 42, Green Valley Agricultural Zone, Pune, India"
        )
        db.add(farmer)
        db.flush()

        # 2. Create Demo Field
        field = Field(
            farmer_id=farmer.id,
            name="North Valley Wheat Sector",
            latitude=18.5204,
            longitude=73.8567,
            size_hectares=4.5,
            soil_type="Clay Loam"
        )
        db.add(field)
        db.flush()

        # 3. Create Demo Crop
        crop = Crop(
            field_id=field.id,
            crop_type="Wheat (HD-2967)",
            growth_stage="Vegetative",
            planted_date=date.today() - timedelta(days=25),
            expected_harvest_date=date.today() + timedelta(days=95),
            kc_factor=1.15,
            is_active=True
        )
        db.add(crop)

        # 4. Create Demo Sensors
        sensor1 = Sensor(
            id="SEN-WHEAT-01",
            field_id=field.id,
            sensor_type="soil_moisture",
            model_name="SoilOptix-Capacitive-Pro",
            status="active",
            battery_level=98.5,
            last_seen=datetime.now(timezone.utc)
        )
        sensor2 = Sensor(
            id="SEN-WHEAT-02",
            field_id=field.id,
            sensor_type="soil_moisture",
            model_name="SoilOptix-Capacitive-Pro",
            status="active",
            battery_level=94.0,
            last_seen=datetime.now(timezone.utc)
        )
        db.add_all([sensor1, sensor2])
        db.commit()
        logger.info("Demo database seeded successfully with 1 Farmer, 1 Field, 1 Crop, and 2 Sensors.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_db()
    seed_db()
