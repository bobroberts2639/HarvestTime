"""
Harvest Time — Data Model
=========================
SQLAlchemy models for PostGIS-backed backend.
20 entities matching Alembic migration 001_initial_schema.

PostGIS: Geography columns (SRID 4326) for spatial queries.
- Farm.location → Geography(POINT, 4326)
- Field.location → Geography(POINT, 4326)
- Field.boundary → Geography(POLYGON, 4326)
- WeatherStation.location → Geography(POINT, 4326)

Authority: Forge's migration is the source of truth for table structure.
This file must match `alembic/versions/001_initial_schema.py` exactly.
"""

from __future__ import annotations

import enum
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from geoalchemy2 import Geography
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class CropType(str, enum.Enum):
    WHEAT = "wheat"
    CORN = "corn"
    SOYBEAN = "soybean"
    RICE = "rice"
    COTTON = "cotton"
    BARLEY = "barley"
    OATS = "oats"
    SORGHUM = "sorghum"
    POTATO = "potato"
    TOMATO = "tomato"
    CITRUS = "citrus"
    APPLE = "apple"
    GRAPE = "grape"
    OTHER = "other"


class GrowthStage(str, enum.Enum):
    DORMANT = "dormant"
    EMERGENCE = "emergence"
    TILLERING = "tillering"
    JOINTING = "jointing"
    HEADING = "heading"
    FLOWERING = "flowering"
    FRUIT_FILL = "fruit_fill"
    MATURATION = "maturation"
    HARVEST_READY = "harvest_ready"
    POST_HARVEST = "post_harvest"


class SoilType(str, enum.Enum):
    SANDY = "sandy"
    LOAM = "loam"
    CLAY = "clay"
    SILT = "silt"
    PEATY = "peaty"
    CHALKY = "chalky"
    SILTY_LOAM = "silty_loam"
    SANDY_LOAM = "sandy_loam"
    CLAY_LOAM = "clay_loam"


class DrainageClass(str, enum.Enum):
    EXCESSIVE = "excessive"
    WELL_DRAINED = "well_drained"
    MODERATELY_DRAINED = "moderately_drained"
    POORLY_DRAINED = "poorly_drained"
    VERY_POORLY_DRAINED = "very_poorly_drained"


class AlertType(str, enum.Enum):
    FROST = "frost"
    HEAT_STRESS = "heat_stress"
    SEVERE_STORM = "severe_storm"
    HIGH_WIND = "high_wind"
    HEAVY_RAIN = "heavy_rain"
    DROUGHT = "drought"
    HAIL = "hail"


class AlertSeverity(str, enum.Enum):
    INFO = "info"
    WATCH = "watch"
    WARNING = "warning"
    CRITICAL = "critical"


class RecommendationPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class RecommendationCategory(str, enum.Enum):
    IRRIGATION = "irrigation"
    FERTILIZATION = "fertilization"
    PEST_CONTROL = "pest_control"
    PLANTING = "planting"
    HARVESTING = "harvesting"
    TILLAGE = "tillage"
    DRAINAGE = "drainage"
    FROST_PROTECTION = "frost_protection"
    OTHER = "other"


class EventType(str, enum.Enum):
    PLANTING = "planting"
    FERTILIZER_APPLICATION = "fertilizer_application"
    IRRIGATION = "irrigation"
    HARVEST = "harvest"
    TILLAGE = "tillage"
    PEST_CONTROL = "pest_control"
    SCOUTING = "scouting"
    SOIL_SAMPLE = "soil_sample"
    OTHER = "other"


class FeedbackSentiment(str, enum.Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


# ---------------------------------------------------------------------------
# Core Entities
# ---------------------------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    display_name = Column(String(128), nullable=False)
    phone = Column(String(32), nullable=True)
    timezone = Column(String(64), nullable=False, default="UTC")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    farms = relationship("Farm", back_populates="owner", cascade="all, delete-orphan")
    preferences = relationship("UserPreferences", back_populates="user", uselist=False, cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="user")
    custom_events = relationship("CustomEvent", back_populates="user")
    overrides = relationship("UserOverride", back_populates="user")
    alert_thresholds = relationship("AlertThreshold", back_populates="user", cascade="all, delete-orphan")


class Farm(Base):
    __tablename__ = "farms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Farm centroid — used for regional weather zone assignment
    location = Column(Geography(geometry_type="POINT", srid=4326), nullable=True)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    owner = relationship("User", back_populates="farms")
    fields = relationship("Field", back_populates="farm", cascade="all, delete-orphan")


class Field(Base):
    __tablename__ = "fields"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id = Column(UUID(as_uuid=True), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)

    # PostGIS geography — field centroid for spatial queries
    location = Column(Geography(geometry_type="POINT", srid=4326), nullable=False)

    # Optional: field boundary polygon for precision agriculture
    boundary = Column(Geography(geometry_type="POLYGON", srid=4326), nullable=True)

    # Area in hectares
    area_hectares = Column(Float, nullable=True)

    # Tags for flexible categorization
    tags = Column(ARRAY(String), nullable=True)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    farm = relationship("Farm", back_populates="fields")
    forecasts = relationship("WeatherForecast", back_populates="field", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="field", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="field")
    field_notes = relationship("FieldNote", back_populates="field", cascade="all, delete-orphan")
    custom_events = relationship("CustomEvent", back_populates="field")
    gdd_records = relationship("GrowingDegreeDay", back_populates="field", cascade="all, delete-orphan")
    season_journals = relationship("SeasonJournal", back_populates="field", cascade="all, delete-orphan")
    overrides = relationship("UserOverride", back_populates="field", cascade="all, delete-orphan")
    crop_plantings = relationship("CropPlanting", back_populates="field", cascade="all, delete-orphan")
    soil_profiles = relationship("SoilProfile", back_populates="field", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_fields_farm", "farm_id"),
        Index("idx_fields_location", "location", postgresql_using="gist"),
    )


# ---------------------------------------------------------------------------
# Crop & Soil Entities (normalized from Field)
# ---------------------------------------------------------------------------

class Crop(Base):
    """Reference table for crop types — lookup data for the recommendation engine."""
    __tablename__ = "crops"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)       # e.g. "Winter Wheat"
    crop_type = Column(Enum(CropType), nullable=False)
    variety = Column(String(255), nullable=True)                  # e.g. "Hard Red Winter"
    base_temp_c = Column(Float, nullable=True)                    # GDD base temperature
    growing_season_days = Column(Integer, nullable=True)          # typical days to maturity
    description = Column(Text, nullable=True)
    tags = Column(ARRAY(String), nullable=True)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    plantings = relationship("CropPlanting", back_populates="crop")


class CropPlanting(Base):
    """Active or historical crop plantings on a field."""
    __tablename__ = "crop_plantings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_id = Column(UUID(as_uuid=True), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    crop_id = Column(UUID(as_uuid=True), ForeignKey("crops.id"), nullable=False)
    planting_date = Column(Date, nullable=False)
    expected_harvest_date = Column(Date, nullable=True)
    actual_harvest_date = Column(Date, nullable=True)
    growth_stage = Column(Enum(GrowthStage), nullable=True)
    is_active = Column(Boolean, default=True)
    tags = Column(ARRAY(String), nullable=True)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    field = relationship("Field", back_populates="crop_plantings")
    crop = relationship("Crop", back_populates="plantings")

    __table_args__ = (
        Index("idx_plantings_field_active", "field_id", "is_active"),
    )


class SoilProfile(Base):
    """Soil data per field — can have multiple historical samples."""
    __tablename__ = "soil_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_id = Column(UUID(as_uuid=True), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    sample_date = Column(Date, nullable=False)

    soil_type = Column(Enum(SoilType), nullable=True)
    drainage_class = Column(Enum(DrainageClass), nullable=True)
    organic_matter_pct = Column(Float, nullable=True)
    ph = Column(Float, nullable=True)
    nitrogen_ppm = Column(Float, nullable=True)
    phosphorus_ppm = Column(Float, nullable=True)
    potassium_ppm = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)

    # Source of soil data: "ssurgo", "soilgrids", "manual", "farmer"
    source = Column(String(64), nullable=True)
    tags = Column(ARRAY(String), nullable=True)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    field = relationship("Field", back_populates="soil_profiles")

    __table_args__ = (
        Index("idx_soil_field_date", "field_id", "sample_date"),
    )


# ---------------------------------------------------------------------------
# Weather Entities
# ---------------------------------------------------------------------------

class WeatherStation(Base):
    """Reference table for weather stations — used for spatial proximity queries."""
    __tablename__ = "weather_stations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    station_id = Column(String(32), unique=True, nullable=False)
    name = Column(String(255), nullable=True)
    source = Column(String(64), nullable=False)

    location = Column(Geography(geometry_type="POINT", srid=4326), nullable=False)

    elevation_m = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    tags = Column(ARRAY(String), nullable=True)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("idx_stations_location", "location", postgresql_using="gist"),
    )


class WeatherObservation(Base):
    """Raw historical weather observations from stations."""
    __tablename__ = "weather_observations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    station_id = Column(UUID(as_uuid=True), ForeignKey("weather_stations.id"), nullable=False)
    observed_at = Column(DateTime(timezone=True), nullable=False)

    temperature_c = Column(Float, nullable=True)
    humidity_pct = Column(Float, nullable=True)
    precipitation_mm = Column(Float, nullable=True)
    wind_speed_kph = Column(Float, nullable=True)
    wind_gust_kph = Column(Float, nullable=True)
    wind_direction = Column(String(4), nullable=True)
    cloud_cover_pct = Column(Float, nullable=True)
    uv_index = Column(Float, nullable=True)
    solar_radiation_mj = Column(Float, nullable=True)
    soil_temp_10cm_c = Column(Float, nullable=True)

    tags = Column(ARRAY(String), nullable=True)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("idx_observations_station_time", "station_id", "observed_at"),
    )


class WeatherForecast(Base):
    __tablename__ = "weather_forecasts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_id = Column(UUID(as_uuid=True), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    station_id = Column(UUID(as_uuid=True), ForeignKey("weather_stations.id"), nullable=True)
    source = Column(String(64), nullable=False)
    forecast_date = Column(Date, nullable=False)
    issued_at = Column(DateTime(timezone=True), nullable=False)

    temperature_high_c = Column(Float, nullable=True)
    temperature_low_c = Column(Float, nullable=True)
    precipitation_mm = Column(Float, nullable=True)
    precipitation_probability = Column(Float, nullable=True)
    humidity_pct = Column(Float, nullable=True)
    wind_speed_kph = Column(Float, nullable=True)
    wind_gust_kph = Column(Float, nullable=True)
    wind_direction = Column(String(4), nullable=True)
    cloud_cover_pct = Column(Float, nullable=True)
    uv_index = Column(Float, nullable=True)
    solar_radiation_mj = Column(Float, nullable=True)

    # Agricultural context (computed by weather module)
    spray_window_hours = Column(Float, nullable=True)
    frost_risk = Column(Boolean, default=False)
    heat_stress_risk = Column(Boolean, default=False)

    tags = Column(ARRAY(String), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    field = relationship("Field", back_populates="forecasts")

    __table_args__ = (
        Index("idx_forecasts_field_date", "field_id", "forecast_date", unique=True),
    )


# ---------------------------------------------------------------------------
# Alert Entities
# ---------------------------------------------------------------------------

class Alert(Base):
    """Weather alerts — frost, heat, storms. Crop-specific impact."""
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_id = Column(UUID(as_uuid=True), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    alert_type = Column(Enum(AlertType), nullable=False)
    severity = Column(Enum(AlertSeverity), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    source = Column(String(64), nullable=False)

    starts_at = Column(DateTime(timezone=True), nullable=False)
    ends_at = Column(DateTime(timezone=True), nullable=True)

    # Crop-specific context
    crop_impact = Column(Text, nullable=True)
    recommended_action = Column(Text, nullable=True)

    acknowledged = Column(Boolean, default=False)
    tags = Column(ARRAY(String), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    field = relationship("Field", back_populates="alerts")

    __table_args__ = (
        Index("idx_alerts_field_time", "field_id", "starts_at"),
    )


class AlertThreshold(Base):
    """User-configurable alert thresholds per field or globally."""
    __tablename__ = "alert_thresholds"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Nullable field_id — null means global threshold for all fields
    field_id = Column(UUID(as_uuid=True), ForeignKey("fields.id", ondelete="CASCADE"), nullable=True)

    alert_type = Column(Enum(AlertType), nullable=False)
    threshold_value = Column(Float, nullable=True)                  # e.g. -2.0 for frost
    is_enabled = Column(Boolean, default=True)
    tags = Column(ARRAY(String), nullable=True)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="alert_thresholds")

    __table_args__ = (
        Index("idx_thresholds_user_field", "user_id", "field_id"),
    )


# ---------------------------------------------------------------------------
# Recommendation Entities
# ---------------------------------------------------------------------------

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    field_id = Column(UUID(as_uuid=True), ForeignKey("fields.id"), nullable=False)

    category = Column(Enum(RecommendationCategory), nullable=False)
    priority = Column(Enum(RecommendationPriority), nullable=False)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)

    # Reasoning powers the "Why?" feature
    reasoning = Column(Text, nullable=True)
    # Confidence: 0.0-1.0
    confidence = Column(Float, nullable=True)

    # Time sensitivity
    valid_from = Column(DateTime(timezone=True), nullable=True)
    valid_until = Column(DateTime(timezone=True), nullable=True)

    # Weather inputs that drove this recommendation
    weather_summary = Column(JSONB, nullable=True)

    # State
    is_active = Column(Boolean, default=True)
    is_snoozed = Column(Boolean, default=False)
    snoozed_until = Column(DateTime(timezone=True), nullable=True)
    is_dismissed = Column(Boolean, default=False)

    tags = Column(ARRAY(String), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    user = relationship("User", back_populates="recommendations")
    field = relationship("Field", back_populates="recommendations")
    feedback = relationship("RecommendationFeedback", back_populates="recommendation", uselist=False)

    __table_args__ = (
        Index("idx_recs_user_active", "user_id", "is_active"),
        Index("idx_recs_field_created", "field_id", "created_at"),
    )


class RecommendationFeedback(Base):
    """User sentiment on each recommendation."""
    __tablename__ = "recommendation_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recommendation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("recommendations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    sentiment = Column(Enum(FeedbackSentiment), nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    recommendation = relationship("Recommendation", back_populates="feedback")


# ---------------------------------------------------------------------------
# Seasonal Planning
# ---------------------------------------------------------------------------

class SeasonalPlan(Base):
    """Long-range seasonal planning — climate outlooks mapped to schedules."""
    __tablename__ = "seasonal_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    field_id = Column(UUID(as_uuid=True), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)

    season_year = Column(Integer, nullable=False)
    crop_type = Column(Enum(CropType), nullable=False)
    crop_variety = Column(String(255), nullable=True)

    # Climate outlook
    outlook_summary = Column(Text, nullable=True)
    planting_window_start = Column(Date, nullable=True)
    planting_window_end = Column(Date, nullable=True)
    harvest_window_start = Column(Date, nullable=True)
    harvest_window_end = Column(Date, nullable=True)

    # Rotation recommendations based on soil health
    rotation_notes = Column(Text, nullable=True)

    # Structured plan data
    plan_data = Column(JSONB, nullable=True)
    tags = Column(ARRAY(String), nullable=True)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_seasonal_field_year", "field_id", "season_year"),
    )


# ---------------------------------------------------------------------------
# Ownership Layer — V1
# ---------------------------------------------------------------------------

class UserPreferences(Base):
    """V1 — user-level preferences."""
    __tablename__ = "user_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    # Units
    temperature_unit = Column(String(1), nullable=False, default="C")
    precipitation_unit = Column(String(2), nullable=False, default="mm")

    # Language
    language = Column(String(10), nullable=False, default="en")

    # Notifications
    frost_alerts_enabled = Column(Boolean, default=True)
    heat_alerts_enabled = Column(Boolean, default=True)
    storm_alerts_enabled = Column(Boolean, default=True)
    weekly_briefing_enabled = Column(Boolean, default=True)
    quiet_hours_start = Column(String(5), nullable=True)
    quiet_hours_end = Column(String(5), nullable=True)

    tags = Column(ARRAY(String), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="preferences")


class CustomEvent(Base):
    """V1 — farmer-logged field events."""
    __tablename__ = "custom_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    field_id = Column(UUID(as_uuid=True), ForeignKey("fields.id"), nullable=False)
    event_type = Column(Enum(EventType), nullable=False)
    event_date = Column(Date, nullable=False)
    notes = Column(Text, nullable=True)
    metadata = Column(JSONB, nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    user = relationship("User", back_populates="custom_events")
    field = relationship("Field", back_populates="custom_events")

    __table_args__ = (
        Index("idx_events_field_date", "field_id", "event_date"),
    )


# ---------------------------------------------------------------------------
# Ownership Layer — V2
# ---------------------------------------------------------------------------

class FieldNote(Base):
    """V2 — free-form notes per field, per date, with photo attachment."""
    __tablename__ = "field_notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_id = Column(UUID(as_uuid=True), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    note_date = Column(Date, nullable=False)
    body = Column(Text, nullable=False)
    photo_key = Column(String(255), nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    field = relationship("Field", back_populates="field_notes")

    __table_args__ = (
        Index("idx_notes_field_date", "field_id", "note_date"),
    )


class SeasonJournal(Base):
    """V2 — end-of-season summary per field."""
    __tablename__ = "season_journals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_id = Column(UUID(as_uuid=True), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    season_year = Column(Integer, nullable=False)
    crop_type = Column(Enum(CropType), nullable=False)
    crop_variety = Column(String(255), nullable=True)

    # Auto-generated from CustomEvents + FieldNotes + Feedback
    summary = Column(Text, nullable=True)
    yield_actual = Column(Float, nullable=True)
    yield_unit = Column(String(32), nullable=True)
    notes = Column(Text, nullable=True)
    tags = Column(ARRAY(String), nullable=True)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    field = relationship("Field", back_populates="season_journals")

    __table_args__ = (
        UniqueConstraint("field_id", "season_year", name="uq_journal_field_season"),
    )


class UserOverride(Base):
    """V2/V3 — user overrides that influence the recommendation engine."""
    __tablename__ = "user_overrides"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    field_id = Column(UUID(as_uuid=True), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)

    override_type = Column(String(64), nullable=False)
    override_key = Column(String(128), nullable=False)
    override_value = Column(JSONB, nullable=False)

    # For advanced V3+ personal rules
    rule_description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    tags = Column(ARRAY(String), nullable=True)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="overrides")
    field = relationship("Field", back_populates="overrides")

    __table_args__ = (
        Index("idx_overrides_field", "field_id"),
    )


# ---------------------------------------------------------------------------
# Agronomic Tracking
# ---------------------------------------------------------------------------

class GrowingDegreeDay(Base):
    """GDD accumulator per field/crop — drives growth stage predictions."""
    __tablename__ = "growing_degree_days"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_id = Column(UUID(as_uuid=True), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    crop_type = Column(Enum(CropType), nullable=False)
    record_date = Column(Date, nullable=False)

    base_temp_c = Column(Float, nullable=False)
    max_temp_c = Column(Float, nullable=False)
    min_temp_c = Column(Float, nullable=False)
    gdd_accumulated = Column(Float, nullable=False)
    gdd_daily = Column(Float, nullable=False)

    tags = Column(ARRAY(String), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    field = relationship("Field", back_populates="gdd_records")

    __table_args__ = (
        Index("idx_gdd_field_date", "field_id", "record_date", unique=True),
    )
