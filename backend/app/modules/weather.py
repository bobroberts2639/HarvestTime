"""Weather module — API routes for weather data and forecasts.

Real lat/lng extraction from PostGIS GEOGRAPHY columns.
Frost risk checks forecast lows, not just current temp.
"""

from uuid import UUID
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Field, Farm
from app.modules.weather_service import WeatherService

router = APIRouter(prefix="/api/v1/weather", tags=["weather"])


async def _resolve_field_coords(field_id: UUID, db: AsyncSession) -> tuple[float, float]:
    """Resolve field coordinates by checking farm location."""
    result = await db.execute(select(Field).where(Field.id == field_id))
    field = result.scalar_one_or_none()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")

    # Get farm location coordinates via PostGIS ST_X/ST_Y
    result = await db.execute(
        select(
            func.ST_X(Farm.location).label("lng"),
            func.ST_Y(Farm.location).label("lat"),
        ).where(Farm.id == field.farm_id)
    )
    row = result.one_or_none()
    if row and row.lat is not None and row.lng is not None:
        return (float(row.lat), float(row.lng))

    raise HTTPException(
        status_code=400,
        detail="Field has no resolved coordinates. Set farm location first.",
    )


@router.get("/{field_id}/forecast")
async def get_field_forecast(
    field_id: UUID,
    days: int = Query(default=7, ge=1, le=14),
    db: AsyncSession = Depends(get_db),
):
    """Get weather forecast for a specific field."""
    lat, lng = await _resolve_field_coords(field_id, db)
    service = WeatherService(db)
    forecasts = await service.get_forecast(field_id, lat, lng, days)

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
async def get_current_conditions(field_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get current weather conditions for a field."""
    lat, lng = await _resolve_field_coords(field_id, db)
    service = WeatherService(db)
    conditions = await service.get_current_conditions(lat, lng)
    return {"field_id": str(field_id), "conditions": conditions}


@router.get("/{field_id}/frost-risk")
async def check_frost_risk(
    field_id: UUID,
    crop_type: str = Query(default="corn"),
    custom_threshold: float | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Check frost risk for a field's crop."""
    lat, lng = await _resolve_field_coords(field_id, db)
    service = WeatherService(db)
    risk = await service.check_frost_risk(lat, lng, crop_type, custom_threshold)
    return {"field_id": str(field_id), "crop_type": crop_type, "frost_risk": risk}


@router.get("/{field_id}/spray-window")
async def check_spray_window(field_id: UUID, db: AsyncSession = Depends(get_db)):
    """Identify spray-compatible weather windows for a field."""
    lat, lng = await _resolve_field_coords(field_id, db)
    service = WeatherService(db)
    forecasts = await service.get_forecast(field_id, lat, lng, days=3)

    spray_windows = []
    for f in forecasts:
        # Spray conditions: low wind (< 15 kph), no rain, moderate humidity
        is_suitable = (
            f.wind_speed_kmh and f.wind_speed_kmh < 15
            and f.precipitation_probability_pct and f.precipitation_probability_pct < 30
        )
        if is_suitable:
            spray_windows.append({
                "date": str(f.forecast_date),
                "wind_kph": f.wind_speed_kmh,
                "rain_probability": f.precipitation_probability_pct,
            })

    return {
        "field_id": str(field_id),
        "windows": spray_windows,
        "count": len(spray_windows),
    }
