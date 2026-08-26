import json
import logging
from datetime import datetime, timezone
import httpx
from backend.app.services.weather.adapter import WeatherProviderAdapter, WeatherResult

logger = logging.getLogger(__name__)

class TomorrowIOAdapter(WeatherProviderAdapter):
    """
    Tomorrow.io API integration adapter (fallback provider).
    """
    TIMELINES_URL = "https://api.tomorrow.io/v4/timelines"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def get_current_and_forecast(self, latitude: float, longitude: float) -> WeatherResult:
        if not self.api_key:
            raise ValueError("Tomorrow.io API key is not configured.")

        params = {
            "location": f"{latitude},{longitude}",
            "fields": ["temperature", "humidity", "precipitationIntensity", "precipitationProbability", "windSpeed", "solarGHI"],
            "units": "metric",
            "timesteps": ["current", "1h"],
            "apikey": self.api_key
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(self.TIMELINES_URL, params=params)
            if res.status_code != 200:
                raise RuntimeError(f"Tomorrow.io API returned status {res.status_code}")

            data = res.json()
            intervals = data.get("data", {}).get("timelines", [{}])[0].get("intervals", [])
            current_vals = intervals[0].get("values", {}) if intervals else {}

            return WeatherResult(
                temperature=float(current_vals.get("temperature", 25.0)),
                humidity=float(current_vals.get("humidity", 50.0)),
                rainfall_1h=float(current_vals.get("precipitationIntensity", 0.0)),
                rainfall_24h=float(current_vals.get("precipitationIntensity", 0.0)) * 24.0,
                rain_probability=float(current_vals.get("precipitationProbability", 0.0)),
                wind_speed=float(current_vals.get("windSpeed", 0.0)),
                solar_radiation=float(current_vals.get("solarGHI", 500.0)),
                forecast_json=json.dumps(intervals[:8]),
                provider="tomorrow_io",
                timestamp=datetime.now(timezone.utc)
            )
