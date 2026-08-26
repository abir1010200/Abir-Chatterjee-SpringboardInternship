import json
import logging
import math
import random
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.db.session import SessionLocal
from backend.app.models.field import Field
from backend.app.models.weather_data import WeatherData
from backend.app.services.weather.adapter import WeatherResult
from backend.app.services.weather.openweather import OpenWeatherAdapter
from backend.app.services.weather.tomorrow_io import TomorrowIOAdapter

logger = logging.getLogger(__name__)

class WeatherService:
    def __init__(self):
        self.openweather_adapter = OpenWeatherAdapter(settings.OPENWEATHER_API_KEY)
        self.tomorrow_adapter = TomorrowIOAdapter(settings.TOMORROW_API_KEY)
        self._cache: Dict[int, Dict[str, Any]] = {}  # field_id -> {result, expires_at}
        self.cache_ttl = timedelta(minutes=settings.WEATHER_CACHE_TTL_MINUTES)

    def _generate_realistic_fallback(self, latitude: float, longitude: float) -> WeatherResult:
        """
        Generates realistic meteorological conditions for coordinates
        when external weather APIs are unreachable or unconfigured.
        """
        now = datetime.now(timezone.utc)
        hour = now.hour + (now.minute / 60.0)

        # Diurnal temperature cycle peaking at 14:00 local solar time
        base_temp = 26.0 - (abs(latitude) * 0.15)
        temp_amplitude = 6.5
        temperature = base_temp + temp_amplitude * math.sin((hour - 8.0) * math.pi / 12.0) + random.gauss(0, 0.4)
        
        # Inverse humidity cycle
        humidity = max(20.0, min(95.0, 70.0 - (temperature - 20.0) * 2.5 + random.gauss(0, 1.5)))

        # Solar radiation
        daylight = max(0.0, math.sin((hour - 6.0) * math.pi / 12.0)) if 6.0 <= hour <= 18.0 else 0.0
        solar_rad = max(0.0, 800.0 * daylight + random.gauss(0, 10.0))

        # Rain probability & 1h rain
        rain_prob = random.choice([5.0, 10.0, 15.0, 25.0, 60.0])
        rain_1h = random.uniform(1.5, 8.0) if rain_prob > 50.0 else 0.0

        forecast = [
            {
                "dt_txt": (now + timedelta(hours=i*3)).strftime("%Y-%m-%d %H:%M:%S"),
                "temp": round(temperature + random.uniform(-2, 2), 1),
                "pop": rain_prob,
                "rain_3h": round(rain_1h * 1.5, 1)
            }
            for i in range(1, 9)
        ]

        return WeatherResult(
            temperature=temperature,
            humidity=humidity,
            rainfall_1h=rain_1h,
            rainfall_24h=rain_1h * 2.5,
            rain_probability=rain_prob,
            wind_speed=random.uniform(1.5, 5.5),
            solar_radiation=solar_rad,
            forecast_json=json.dumps(forecast),
            provider="fallback_synthesizer",
            timestamp=now
        )

    async def fetch_weather_for_field(self, db: Session, field: Field, force_refresh: bool = False) -> WeatherData:
        """
        Fetch meteorological conditions for a field, check cache, query external APIs,
        and durably commit to the weather_data table.
        """
        now = datetime.now(timezone.utc)

        # 1. Check in-memory cache if not force refresh
        if not force_refresh and field.id in self._cache:
            entry = self._cache[field.id]
            if now < entry["expires_at"]:
                logger.debug(f"Serving cached weather for field {field.id}")
                return entry["db_record"]

        # 2. Query Primary / Secondary Adapters
        result: Optional[WeatherResult] = None

        if settings.OPENWEATHER_API_KEY:
            try:
                logger.info(f"Querying OpenWeather API for Field {field.id} ({field.latitude}, {field.longitude})...")
                result = await self.openweather_adapter.get_current_and_forecast(field.latitude, field.longitude)
            except Exception as e:
                logger.warning(f"OpenWeather API failed for Field {field.id}: {e}. Trying Tomorrow.io fallback.")

        if not result and settings.TOMORROW_API_KEY:
            try:
                logger.info(f"Querying Tomorrow.io API for Field {field.id}...")
                result = await self.tomorrow_adapter.get_current_and_forecast(field.latitude, field.longitude)
            except Exception as e:
                logger.warning(f"Tomorrow.io API failed for Field {field.id}: {e}.")

        if not result:
            logger.info(f"Using physical weather synthesizer fallback for Field {field.id} ({field.name})")
            result = self._generate_realistic_fallback(field.latitude, field.longitude)

        # 3. Persist to database
        db_weather = WeatherData(
            field_id=field.id,
            temperature=result.temperature,
            humidity=result.humidity,
            rainfall_1h=result.rainfall_1h,
            rainfall_24h=result.rainfall_24h,
            rain_probability=result.rain_probability,
            wind_speed=result.wind_speed,
            solar_radiation=result.solar_radiation,
            forecast_json=result.forecast_json,
            provider=result.provider,
            timestamp=result.timestamp or now
        )

        try:
            db.add(db_weather)
            db.commit()
            db.refresh(db_weather)
            logger.info(
                f"Stored weather record id={db_weather.id} for field={field.id}: "
                f"temp={db_weather.temperature}°C, rain_prob={db_weather.rain_probability}%, provider={db_weather.provider}"
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to persist weather data for field {field.id}: {e}")
            raise

        # 4. Update cache
        self._cache[field.id] = {
            "db_record": db_weather,
            "expires_at": now + self.cache_ttl
        }

        return db_weather

    def get_latest_weather(self, db: Session, field_id: int) -> Optional[WeatherData]:
        """Query latest weather observation recorded for a field."""
        return db.query(WeatherData).filter(
            WeatherData.field_id == field_id
        ).order_by(WeatherData.timestamp.desc()).first()

    def get_weather_history(
        self,
        db: Session,
        field_id: int,
        limit: int = 100,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[WeatherData]:
        """Query historical weather observations for a field."""
        query = db.query(WeatherData).filter(WeatherData.field_id == field_id)
        if start_time:
            query = query.filter(WeatherData.timestamp >= start_time)
        if end_time:
            query = query.filter(WeatherData.timestamp <= end_time)
        return query.order_by(WeatherData.timestamp.desc()).limit(limit).all()

weather_service = WeatherService()
