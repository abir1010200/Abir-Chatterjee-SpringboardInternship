from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import String, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.session import Base

class Field(Base):
    __tablename__ = "fields"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    farmer_id: Mapped[int] = mapped_column(ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    size_hectares: Mapped[float] = mapped_column(Float, nullable=False)
    soil_type: Mapped[str] = mapped_column(String(50), nullable=False, default="Loam")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    farmer: Mapped["Farmer"] = relationship("Farmer", back_populates="fields")
    crops: Mapped[List["Crop"]] = relationship("Crop", back_populates="field", cascade="all, delete-orphan")
    sensors: Mapped[List["Sensor"]] = relationship("Sensor", back_populates="field", cascade="all, delete-orphan")
    sensor_readings: Mapped[List["SensorReading"]] = relationship("SensorReading", back_populates="field", cascade="all, delete-orphan")
    weather_data: Mapped[List["WeatherData"]] = relationship("WeatherData", back_populates="field", cascade="all, delete-orphan")
    irrigation_history: Mapped[List["IrrigationHistory"]] = relationship("IrrigationHistory", back_populates="field", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Field(id={self.id}, name='{self.name}', farmer_id={self.farmer_id}, size={self.size_hectares}ha)>"
