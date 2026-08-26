from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.app.db.session import Base

class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sensor_id = Column(String(50), ForeignKey("sensors.id", ondelete="CASCADE"), nullable=False, index=True)
    field_id = Column(Integer, ForeignKey("fields.id", ondelete="CASCADE"), nullable=False, index=True)
    soil_moisture = Column(Float, nullable=False)  # % volumetric or relative (0 - 100%)
    temperature_soil = Column(Float, nullable=True)  # °C
    battery_level = Column(Float, nullable=True)  # %
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    is_valid = Column(Boolean, default=True, nullable=False)
    cleaning_flag = Column(String(50), default="raw", nullable=False)  # raw, cleaned, interpolated, outlier_clipped
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    sensor = relationship("Sensor", back_populates="readings")
    field = relationship("Field", back_populates="sensor_readings")

    # Time-series Indexes & Idempotency Constraints
    __table_args__ = (
        UniqueConstraint("sensor_id", "timestamp", name="uq_sensor_timestamp"),
        Index("idx_sensor_readings_field_time", "field_id", "timestamp"),
        Index("idx_sensor_readings_sensor_time", "sensor_id", "timestamp"),
    )

    def __repr__(self):
        return f"<SensorReading(id={self.id}, sensor='{self.sensor_id}', field={self.field_id}, moisture={self.soil_moisture}%, time={self.timestamp})>"
