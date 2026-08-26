from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Float, DateTime, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.session import Base

class WeatherData(Base):
    __tablename__ = "weather_data"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    field_id: Mapped[int] = mapped_column(ForeignKey("fields.id", ondelete="CASCADE"), nullable=False, index=True)
    temperature: Mapped[float] = mapped_column(Float, nullable=False)
    humidity: Mapped[float] = mapped_column(Float, nullable=False)
    rainfall_1h: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    rainfall_24h: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    rain_probability: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    wind_speed: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    solar_radiation: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    forecast_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    provider: Mapped[str] = mapped_column(String(50), default="openweather", nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    field: Mapped["Field"] = relationship("Field", back_populates="weather_data")

    # Time-series Index
    __table_args__ = (
        Index("idx_weather_field_time", "field_id", "timestamp"),
    )

    def __repr__(self):
        return f"<WeatherData(id={self.id}, field_id={self.field_id}, temp={self.temperature}°C, rain_prob={self.rain_probability}%, time={self.timestamp})>"
