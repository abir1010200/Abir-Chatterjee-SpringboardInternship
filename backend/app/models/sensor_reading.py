from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Float, Boolean, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.session import Base

class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    sensor_id: Mapped[str] = mapped_column(ForeignKey("sensors.id", ondelete="CASCADE"), nullable=False, index=True)
    field_id: Mapped[int] = mapped_column(ForeignKey("fields.id", ondelete="CASCADE"), nullable=False, index=True)
    soil_moisture: Mapped[float] = mapped_column(Float, nullable=False)
    temperature_soil: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    battery_level: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    cleaning_flag: Mapped[str] = mapped_column(String(50), default="raw", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    sensor: Mapped["Sensor"] = relationship("Sensor", back_populates="readings")
    field: Mapped["Field"] = relationship("Field", back_populates="sensor_readings")

    # Time-series Indexes & Idempotency Constraints
    __table_args__ = (
        UniqueConstraint("sensor_id", "timestamp", name="uq_sensor_timestamp"),
        Index("idx_sensor_readings_field_time", "field_id", "timestamp"),
        Index("idx_sensor_readings_sensor_time", "sensor_id", "timestamp"),
    )

    def __repr__(self):
        return f"<SensorReading(id={self.id}, sensor='{self.sensor_id}', field={self.field_id}, moisture={self.soil_moisture}%, time={self.timestamp})>"
