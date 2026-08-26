from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from backend.app.db.session import Base

class Sensor(Base):
    __tablename__ = "sensors"

    id = Column(String(50), primary_key=True, index=True)  # e.g., SEN-FIELD01-01
    field_id = Column(Integer, ForeignKey("fields.id", ondelete="CASCADE"), nullable=False, index=True)
    sensor_type = Column(String(50), nullable=False, default="soil_moisture")  # soil_moisture, soil_temp_moisture, weather_station
    model_name = Column(String(100), nullable=True, default="Capacitive-FDR-v2")
    install_date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    status = Column(String(20), nullable=False, default="active")  # active, stale, offline, maintenance
    battery_level = Column(Float, nullable=True, default=100.0)  # %
    last_seen = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    field = relationship("Field", back_populates="sensors")
    readings = relationship("SensorReading", back_populates="sensor", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Sensor(id='{self.id}', field_id={self.field_id}, status='{self.status}')>"
