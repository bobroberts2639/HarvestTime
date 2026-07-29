"""Weather service — integration with Open-Meteo API."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.weather import WeatherForecast, WeatherObservation


class WeatherService:
    """Service for fetching and storing weather data from Open-Meteo."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.base_url = settings.open_meteo_base_url

    async def get_forecast(
        self,
        field_id: UUID,
        latitude: float,
        longitude: float,
        days: int = 7,
    ) -> list[WeatherForecast]:
        """Fetch 7-day forecast from Open-Meteo and store in DB."""
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "precipitation_probability_max",
                "wind_speed_10m_max",
                "solar_radiation_max",
            ],
            "timezone": "auto",
            "forecast_days": days,
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/forecast",
                params=params,
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

        daily = data.get("daily", {})
        forecasts = []

        for i, forecast_date in enumerate(daily.get("time", [])):
            forecast = WeatherForecast(
                field_id=field_id,
                forecast_date=date.fromisoformat(forecast_date),
                temperature_high_c=Decimal(str(daily["temperature_2m_max"][i])),
                temperature_low_c=Decimal(str(daily["temperature_2m_min"][i])),
                precipitation_mm=Decimal(str(daily["precipitation_sum"][i])),
                precipitation_probability_pct=Decimal(str(daily["precipitation_probability_max"][i])),
                wind_speed_kmh=Decimal(str(daily["wind_speed_10m_max"][i])),
                solar_radiation_wm2=Decimal(str(daily["solar_radiation_max"][i])) if daily.get("solar_radiation_max", [None])[i] else None,
                source="open-meteo",
                fetched_at=datetime.utcnow(),
                raw_data=data,
            )
            forecasts.append(forecast)

        # Store forecasts
        self.db.add_all(forecasts)
        await self.db.flush()

        return forecasts

    async def get_current_conditions(
        self,
        latitude: float,
        longitude: float,
    ) -> dict:
        """Fetch current weather conditions from Open-Meteo."""
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": [
                "temperature_2m",
                "relative_humidity_2m",
                "precipitation",
                "wind_speed_10m",
                "wind_direction_10m",
            ],
            "timezone": "auto",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/forecast",
                params=params,
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

        current = data.get("current", {})
        return {
            "temperature_c": current.get("temperature_2m"),
            "humidity_pct": current.get("relative_humidity_2m"),
            "precipitation_mm": current.get("precipitation"),
            "wind_speed_kmh": current.get("wind_speed_10m"),
            "wind_direction_deg": current.get("wind_direction_10m"),
        }

    async def check_frost_risk(
        self,
        latitude: float,
        longitude: float,
        crop_type: str,
        custom_threshold: float | None = None,
    ) -> dict:
        """Check for frost risk in the coming days."""
        forecast = await self.get_current_conditions(latitude, longitude)

        # Default frost thresholds by crop type
        default_thresholds = {
            "wheat": -8.0,
            "corn": -1.0,
            "soy": -2.0,
            "cotton": -1.0,
            "rice": 0.0,
            "potato": -1.0,
            "tomato": 0.0,
            "citrus": -2.0,
        }

        threshold = custom_threshold or default_thresholds.get(crop_type, 0.0)

        return {
            "current_temp": forecast.get("temperature_c"),
            "frost_threshold": threshold,
            "risk": forecast.get("temperature_c", 100) <= threshold,
            "threshold_source": "custom" if custom_threshold else "default",
        }
