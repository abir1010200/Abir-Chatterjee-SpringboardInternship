from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

class WeatherResult:
    def __init__(
        self,
        temperature: float,
        humidity: float,
        rainfall_1h: float = 0.0,
        rainfall_24h: float = 0.0,
        rain_probability: float = 0.0,
        wind_speed: Optional[float] = None,
        solar_radiation: Optional[float] = None,
        forecast_json: Optional[str] = None,
        provider: str = "openweather",
        timestamp: Optional[datetime] = None
    ):
        self.temperature = round(temperature, 2)
        self.humidity = round(humidity, 1)
        self.rainfall_1h = round(rainfall_1h, 2)
        self.rainfall_24h = round(rainfall_24h, 2)
        self.rain_probability = round(rain_probability, 1)
        self.wind_speed = round(wind_speed, 2) if wind_speed is not None else None
        self.solar_radiation = round(solar_radiation, 2) if solar_radiation is not None else None
        self.forecast_json = forecast_json
        self.provider = provider
        self.timestamp = timestamp

    def to_dict(self) -> Dict[str, Any]:
        return {
            "temperature": self.temperature,
            "humidity": self.humidity,
            "rainfall_1h": self.rainfall_1h,
            "rainfall_24h": self.rainfall_24h,
            "rain_probability": self.rain_probability,
            "wind_speed": self.wind_speed,
            "solar_radiation": self.solar_radiation,
            "forecast_json": self.forecast_json,
            "provider": self.provider,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }

class WeatherProviderAdapter(ABC):
    """Abstract interface defining required contract for all meteorological data providers."""
    
    @abstractmethod
    async def get_current_and_forecast(self, latitude: float, longitude: float) -> WeatherResult:
        """Fetch current atmospheric metrics and rain probability forecast for coordinates."""
        pass
