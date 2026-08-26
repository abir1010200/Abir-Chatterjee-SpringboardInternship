from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import String, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.session import Base

class Sensor(Base):
    __tablename__ = "sensors"

    id: Mapped[str] = mapped_column(String(50), primary_key=True, index=True)
    field_id: Mapped[int] = mapped_column(ForeignKey("fields.id", ondelete="CASCADE"), nullable=False, index=True)
    sensor_type: Mapped[str] = mapped_column(String(50), nullable=False, default="soil_moisture")
    model_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, default="Capacitive-FDR-v2")
    install_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    battery_level: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=100.0)
    last_seen: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    field: Mapped["Field"] = relationship("Field", back_populates="sensors")
    readings: Mapped[List["SensorReading"]] = relationship("SensorReading", back_populates="sensor", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Sensor(id='{self.id}', field_id={self.field_id}, status='{self.status}')>"
