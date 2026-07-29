"""Weather module entities."""

import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, Numeric, DateTime, Date, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography

from app.database import Base


class WeatherStation(Base):
    """WeatherStation — external API source metadata."""
    __tablename__ = "weather_stations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=True)
    location = Column(Geography(geometry_type="POINT", srid=4326), nullable=True)
    provider = Column(String, nullable=False)  # openweathermap|nws|visualcrossing
    external_id = Column(String, nullable=False)


class WeatherObservation(Base):
    """WeatherObservation — historical/actual weather data."""
    __tablename__ = "weather_observations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_id = Column(UUID(as_uuid=True), ForeignKey("fields.id"), nullable=False, index=True)
    station_id = Column(UUID(as_uuid=True), ForeignKey("weather_stations.id"), nullable=True)
    observed_at = Column(DateTime(timezone=True), nullable=False, index=True)
    temperature_c = Column(Numeric(5, 2), nullable=True)
    humidity_pct = Column(Numeric(5, 2), nullable=True)
    precipitation_mm = Column(Numeric(8, 2), nullable=True)
    wind_speed_kmh = Column(Numeric(6, 2), nullable=True)
    wind_direction_deg = Column(Integer, nullable=True)
    solar_radiation_wm2 = Column(Numeric(7, 2), nullable=True)
    soil_temperature_c = Column(Numeric(5, 2), nullable=True)
    raw_data = Column(JSONB, nullable=True)

    # Relationships
    field = relationship("Field", back_populates="weather_observations")
    station = relationship("WeatherStation")

    __table_args__ = (
        Index("ix_weather_obs_field_date", "field_id", "observed_at"),
    )


class WeatherForecast(Base):
    """WeatherForecast — predicted weather data."""
    __tablename__ = "weather_forecasts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_id = Column(UUID(as_uuid=True), ForeignKey("fields.id"), nullable=False, index=True)
    forecast_date = Column(Date, nullable=False, index=True)
    forecast_hour = Column(Integer, nullable=True)  # null = daily aggregate
    temperature_high_c = Column(Numeric(5, 2), nullable=True)
    temperature_low_c = Column(Numeric(5, 2), nullable=True)
    precipitation_probability_pct = Column(Numeric(5, 2), nullable=True)
    precipitation_mm = Column(Numeric(8, 2), nullable=True)
    humidity_pct = Column(Numeric(5, 2), nullable=True)
    wind_speed_kmh = Column(Numeric(6, 2), nullable=True)
    solar_radiation_wm2 = Column(Numeric(7, 2), nullable=True)
    source = Column(String, nullable=False)
    fetched_at = Column(DateTime(timezone=True), nullable=False)
    raw_data = Column(JSONB, nullable=True)

    # Relationships
    field = relationship("Field", back_populates="weather_forecasts")

    __table_args__ = (
        Index("ix_weather_forecast_field_date", "field_id", "forecast_date"),
    )


class GrowingDegreeDay(Base):
    """GrowingDegreeDay — computed daily GDD for a crop planting."""
    __tablename__ = "growing_degree_days"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_id = Column(UUID(as_uuid=True), ForeignKey("fields.id"), nullable=False, index=True)
    crop_planting_id = Column(UUID(as_uuid=True), ForeignKey("crop_plantings.id"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    max_temp_c = Column(Numeric(5, 2), nullable=False)
    min_temp_c = Column(Numeric(5, 2), nullable=False)
    gdd = Column(Numeric(6, 2), nullable=False)  # Daily GDD
    cumulative_gdd = Column(Numeric(8, 2), nullable=False)  # Running total since planting

    # Relationships
    crop_planting = relationship("CropPlanting", back_populates="growing_degree_days")

    __table_args__ = (
        Index("ix_gdd_planting_date", "crop_planting_id", "date"),
    )
