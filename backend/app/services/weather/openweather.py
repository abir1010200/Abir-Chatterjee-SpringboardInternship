import json
import logging
from datetime import datetime, timezone
import httpx
from backend.app.services.weather.adapter import WeatherProviderAdapter, WeatherResult

logger = logging.getLogger(__name__)

class OpenWeatherAdapter(WeatherProviderAdapter):
    """
    OpenWeather API integration adapter.
    Fetches real-time temperature, humidity, rainfall, and pop (probability of precipitation).
    """
    CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
    FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def get_current_and_forecast(self, latitude: float, longitude: float) -> WeatherResult:
        if not self.api_key:
            raise ValueError("OpenWeather API key is not configured.")

        params_current = {
            "lat": latitude,
            "lon": longitude,
            "appid": self.api_key,
            "units": "metric"
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            # 1. Fetch Current Weather
            curr_res = await client.get(self.CURRENT_URL, params=params_current)
            if curr_res.status_code != 200:
                logger.error(f"OpenWeather Current API error: {curr_res.status_code} - {curr_res.text}")
                raise RuntimeError(f"OpenWeather API returned status {curr_res.status_code}")

            curr_data = curr_res.json()

            # 2. Fetch 5-Day / 3-Hour Forecast for Rain Probability
            params_forecast = {
                "lat": latitude,
                "lon": longitude,
                "appid": self.api_key,
                "units": "metric",
                "cnt": 8  # Next 24 hours (8 intervals of 3 hours)
            }
            forecast_res = await client.get(self.FORECAST_URL, params=params_forecast)
            
            rain_prob_max = 0.0
            rainfall_24h_sum = 0.0
            forecast_summary = []

            if forecast_res.status_code == 200:
                forecast_data = forecast_res.json()
                for item in forecast_data.get("list", []):
                    # pop is probability of precipitation (0.0 to 1.0)
                    pop = item.get("pop", 0.0) * 100.0
                    rain_prob_max = max(rain_prob_max, pop)
                    rain_3h = item.get("rain", {}).get("3h", 0.0)
                    rainfall_24h_sum += rain_3h
                    forecast_summary.append({
                        "dt_txt": item.get("dt_txt"),
                        "temp": item.get("main", {}).get("temp"),
                        "pop": round(pop, 1),
                        "rain_3h": rain_3h
                    })

            # Extract current metrics
            temperature = float(curr_data.get("main", {}).get("temp", 25.0))
            humidity = float(curr_data.get("main", {}).get("humidity", 50.0))
            rainfall_1h = float(curr_data.get("rain", {}).get("1h", 0.0))
            wind_speed = float(curr_data.get("wind", {}).get("speed", 0.0))
            
            # Estimate solar radiation from cloudiness (0 - 100%)
            clouds = float(curr_data.get("clouds", {}).get("all", 20.0))
            solar_rad_est = max(50.0, 850.0 * (1.0 - (clouds / 100.0) * 0.7))

            return WeatherResult(
                temperature=temperature,
                humidity=humidity,
                rainfall_1h=rainfall_1h,
                rainfall_24h=rainfall_24h_sum,
                rain_probability=rain_prob_max,
                wind_speed=wind_speed,
                solar_radiation=solar_rad_est,
                forecast_json=json.dumps(forecast_summary),
                provider="openweather",
                timestamp=datetime.now(timezone.utc)
            )
