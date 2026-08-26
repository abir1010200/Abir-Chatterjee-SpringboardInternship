from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.db.session import Base

class Field(Base):
    __tablename__ = "fields"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    size_hectares = Column(Float, nullable=False)
    soil_type = Column(String(50), nullable=False, default="Loam")  # e.g., Clay, Sandy Loam, Silty Clay, Peat
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    farmer = relationship("Farmer", back_populates="fields")
    crops = relationship("Crop", back_populates="field", cascade="all, delete-orphan")
    sensors = relationship("Sensor", back_populates="field", cascade="all, delete-orphan")
    sensor_readings = relationship("SensorReading", back_populates="field", cascade="all, delete-orphan")
    weather_data = relationship("WeatherData", back_populates="field", cascade="all, delete-orphan")
    irrigation_history = relationship("IrrigationHistory", back_populates="field", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Field(id={self.id}, name='{self.name}', farmer_id={self.farmer_id}, size={self.size_hectares}ha)>"
