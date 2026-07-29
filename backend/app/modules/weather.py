"""Weather module — API routes for weather data and forecasts."""

from uuid import UUID
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Field
from app.modules.weather_service import WeatherService

router = APIRouter(prefix="/api/v1/weather", tags=["weather"])


@router.get("/{field_id}/forecast")
async def get_field_forecast(
    field_id: UUID,
    days: int = Query(default=7, ge=1, le=14),
    db: AsyncSession = Depends(get_db),
):
    """Get weather forecast for a specific field."""
    # Get field location
    result = await db.execute(select(Field).where(Field.id == field_id))
    field = result.scalar_one_or_none()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")

    # TODO: Extract lat/lng from field.location geography
    # For now, use a placeholder (will be replaced with actual geo extraction)
    latitude = 40.0  # placeholder
    longitude = -89.0  # placeholder

    service = WeatherService(db)
    forecasts = await service.get_forecast(field_id, latitude, longitude, days)

    return {
        "field_id": str(field_id),
        "forecasts": [
            {
                "date": str(f.forecast_date),
                "high_c": f.temperature_high_c,
                "low_c": f.temperature_low_c,
                "precipitation_mm": f.precipitation_mm,
                "precipitation_probability_pct": f.precipitation_probability_pct,
                "wind_speed_kmh": f.wind_speed_kmh,
                "solar_radiation_wm2": f.solar_radiation_wm2,
            }
            for f in forecasts
        ],
    }


@router.get("/{field_id}/current")
async def get_current_conditions(
    field_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get current weather conditions for a field."""
    result = await db.execute(select(Field).where(Field.id == field_id))
    field = result.scalar_one_or_none()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")

    latitude = 40.0  # placeholder
    longitude = -89.0  # placeholder

    service = WeatherService(db)
    conditions = await service.get_current_conditions(latitude, longitude)

    return {
        "field_id": str(field_id),
        "conditions": conditions,
    }


@router.get("/{field_id}/frost-risk")
async def check_frost_risk(
    field_id: UUID,
    crop_type: str = Query(default="corn"),
    custom_threshold: float | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Check frost risk for a field's crop."""
    result = await db.execute(select(Field).where(Field.id == field_id))
    field = result.scalar_one_or_none()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")

    latitude = 40.0  # placeholder
    longitude = -89.0  # placeholder

    service = WeatherService(db)
    risk = await service.check_frost_risk(latitude, longitude, crop_type, custom_threshold)

    return {
        "field_id": str(field_id),
        "crop_type": crop_type,
        "frost_risk": risk,
    }
