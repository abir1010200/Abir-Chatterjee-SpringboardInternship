from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index, Text
from sqlalchemy.orm import relationship
from backend.app.db.session import Base

class WeatherData(Base):
    __tablename__ = "weather_data"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    field_id = Column(Integer, ForeignKey("fields.id", ondelete="CASCADE"), nullable=False, index=True)
    temperature = Column(Float, nullable=False)  # °C
    humidity = Column(Float, nullable=False)  # %
    rainfall_1h = Column(Float, default=0.0, nullable=False)  # mm
    rainfall_24h = Column(Float, default=0.0, nullable=False)  # mm
    rain_probability = Column(Float, default=0.0, nullable=False)  # % (0 - 100)
    wind_speed = Column(Float, nullable=True)  # m/s
    solar_radiation = Column(Float, nullable=True)  # W/m² (or estimated direct/diffuse)
    forecast_json = Column(Text, nullable=True)  # Serialized 5-day / 3-hr forecast
    provider = Column(String(50), default="openweather", nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    field = relationship("Field", back_populates="weather_data")

    # Time-series Index
    __table_args__ = (
        Index("idx_weather_field_time", "field_id", "timestamp"),
    )

    def __repr__(self):
        return f"<WeatherData(id={self.id}, field_id={self.field_id}, temp={self.temperature}°C, rain_prob={self.rain_probability}%, time={self.timestamp})>"
