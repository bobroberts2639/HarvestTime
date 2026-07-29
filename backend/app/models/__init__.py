"""Core entity models — shared by all modules."""

import uuid
from datetime import datetime, date
from decimal import Decimal

from sqlalchemy import (
    Column, String, Integer, Numeric, Boolean, Text, DateTime, Date,
    ForeignKey, Index, JSON
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography

from app.database import Base


class TimestampMixin:
    """Mixin that adds created_at and updated_at columns."""
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class User(Base, TimestampMixin):
    """User account — farmer or admin."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    timezone = Column(String, default="UTC", nullable=False)
    preferences = Column(JSONB, default=dict, nullable=False)

    # Relationships
    farms = relationship("Farm", back_populates="user", lazy="selectin")
    preferences_detail = relationship("UserPreferences", back_populates="user", uselist=False, lazy="selectin")


class Farm(Base, TimestampMixin):
    """Farm — a collection of fields under one owner."""
    __tablename__ = "farms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    location = Column(Geography(geometry_type="POINT", srid=4326), nullable=True)
    timezone = Column(String, nullable=True)  # Inherits from User if null

    # Relationships
    user = relationship("User", back_populates="farms")
    fields = relationship("Field", back_populates="farm", lazy="selectin")


class Field(Base, TimestampMixin):
    """Field — a specific plot of land within a farm."""
    __tablename__ = "fields"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id = Column(UUID(as_uuid=True), ForeignKey("farms.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    area_hectares = Column(Numeric(10, 2), nullable=True)
    boundary = Column(Geography(geometry_type="POLYGON", srid=4326), nullable=True)
    metadata_ = Column("metadata", JSONB, default=dict, nullable=False)

    # Relationships
    farm = relationship("Farm", back_populates="fields")
    soil_profiles = relationship("SoilProfile", back_populates="field", lazy="selectin")
    plantings = relationship("CropPlanting", back_populates="field", lazy="selectin")
    weather_observations = relationship("WeatherObservation", back_populates="field", lazy="noload")
    weather_forecasts = relationship("WeatherForecast", back_populates="field", lazy="noload")
    recommendations = relationship("Recommendation", back_populates="field", lazy="noload")
    alerts = relationship("Alert", back_populates="field", lazy="noload")
    notes = relationship("FieldNote", back_populates="field", lazy="noload")


class Crop(Base):
    """Crop — reference/lookup table for crop types."""
    __tablename__ = "crops"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)  # "Winter Wheat", "Corn"
    family = Column(String, nullable=True)  # Poaceae, Fabaceae, etc.
    growing_season_start = Column(Integer, nullable=True)  # Month (1-12)
    growing_season_end = Column(Integer, nullable=True)
    base_gdd_temp = Column(Numeric(5, 2), nullable=True)  # Base temp for GDD calculation
    growth_stages = Column(JSONB, nullable=True)  # [{name, min_gdd, max_gdd, typical_duration_days}]
    water_needs = Column(JSONB, nullable=True)  # {mm_per_day_avg, critical_periods: [...]}
    temp_range = Column(JSONB, nullable=True)  # {min_germination, max_germination, min_growth, max_growth}

    # Relationships
    plantings = relationship("CropPlanting", back_populates="crop", lazy="noload")


class CropPlanting(Base, TimestampMixin):
    """CropPlanting — an active season instance of a crop in a field."""
    __tablename__ = "crop_plantings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_id = Column(UUID(as_uuid=True), ForeignKey("fields.id"), nullable=False, index=True)
    crop_id = Column(UUID(as_uuid=True), ForeignKey("crops.id"), nullable=False, index=True)
    planted_date = Column(Date, nullable=False)
    expected_harvest_date = Column(Date, nullable=True)
    actual_harvest_date = Column(Date, nullable=True)
    variety = Column(String, nullable=True)
    seeding_rate = Column(Numeric(10, 2), nullable=True)
    status = Column(String(20), default="planted", nullable=False)  # planted|growing|harvested|failed
    metadata_ = Column("metadata", JSONB, default=dict, nullable=False)

    # Relationships
    field = relationship("Field", back_populates="plantings")
    crop = relationship("Crop", back_populates="plantings")
    growing_degree_days = relationship("GrowingDegreeDay", back_populates="crop_planting", lazy="noload")
    recommendations = relationship("Recommendation", back_populates="crop_planting", lazy="noload")


class SoilProfile(Base, TimestampMixin):
    """SoilProfile — soil data for a field (supports history via multiple rows)."""
    __tablename__ = "soil_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_id = Column(UUID(as_uuid=True), ForeignKey("fields.id"), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    soil_type = Column(String(20), nullable=True)  # clay|sandy|loam|silt|peat|chalk
    ph = Column(Numeric(3, 1), nullable=True)
    organic_matter_pct = Column(Numeric(5, 2), nullable=True)
    nitrogen_ppm = Column(Numeric, nullable=True)
    phosphorus_ppm = Column(Numeric, nullable=True)
    potassium_ppm = Column(Numeric, nullable=True)
    drainage_class = Column(String(20), nullable=True)  # poor|moderate|well|excessive
    water_holding_capacity = Column(Numeric, nullable=True)
    cec = Column(Numeric, nullable=True)  # Cation exchange capacity
    last_tested_date = Column(Date, nullable=True)
    raw_lab_results = Column(JSONB, default=dict, nullable=False)

    # Relationships
    field = relationship("Field", back_populates="soil_profiles")


# --- Ownership & Personalization Entities ---


class UserPreferences(Base, TimestampMixin):
    """UserPreferences — farmer's personalization settings."""
    __tablename__ = "user_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False, index=True)
    units = Column(String(10), default="metric", nullable=False)  # metric|imperial
    language = Column(String(10), default="en", nullable=False)
    organic_mode = Column(Boolean, default=False, nullable=False)
    seasonal_goals = Column(JSONB, default=list, nullable=False)  # [{goal, priority}]
    recommendation_preferences = Column(JSONB, default=dict, nullable=False)  # {skip_categories: [...]}

    # Relationships
    user = relationship("User", back_populates="preferences_detail")


class AlertThreshold(Base, TimestampMixin):
    """AlertThreshold — custom alert thresholds per crop type."""
    __tablename__ = "alert_thresholds"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    crop_type = Column(String, nullable=True)  # null = global default
    alert_type = Column(String(20), nullable=False)  # frost|heat|drought|flood|wind
    threshold_value = Column(Numeric, nullable=False)
    unit = Column(String(10), nullable=False)

    # Composite index for fast lookup
    __table_args__ = (
        Index("ix_alert_thresholds_user_crop_type", "user_id", "crop_type", "alert_type"),
    )


class FieldNote(Base, TimestampMixin):
    """FieldNote — farmer's observations and context for a field."""
    __tablename__ = "field_notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_id = Column(UUID(as_uuid=True), ForeignKey("fields.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    photo_url = Column(String, nullable=True)
    tags = Column(ARRAY(String), default=list, nullable=False)
    season_year = Column(Integer, nullable=False)

    # Relationships
    field = relationship("Field", back_populates="notes")

    __table_args__ = (
        Index("ix_field_notes_field_season", "field_id", "season_year"),
    )


class SeasonJournal(Base, TimestampMixin):
    """SeasonJournal — season-level reflections."""
    __tablename__ = "season_journals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    season_year = Column(Integer, nullable=False)
    reflections = Column(JSONB, default=dict, nullable=False)
    stats = Column(JSONB, default=dict, nullable=False)

    __table_args__ = (
        Index("ix_season_journals_user_year", "user_id", "season_year", unique=True),
    )


class CustomEvent(Base, TimestampMixin):
    """CustomEvent — farmer's personal calendar events."""
    __tablename__ = "custom_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    field_id = Column(UUID(as_uuid=True), ForeignKey("fields.id"), nullable=True, index=True)
    event_type = Column(String(20), nullable=False)  # labor|equipment|contract|market|custom
    title = Column(String, nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    recurrence = Column(JSONB, nullable=True)

    __table_args__ = (
        Index("ix_custom_events_user_time", "user_id", "start_time", "end_time"),
    )


class UserOverride(Base, TimestampMixin):
    """UserOverride — farmer's explicit overrides of system defaults."""
    __tablename__ = "user_overrides"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    field_id = Column(UUID(as_uuid=True), ForeignKey("fields.id"), nullable=True, index=True)
    override_type = Column(String(20), nullable=False)  # growth_stage|irrigation|threshold|schedule
    override_value = Column(JSONB, nullable=False)

    __table_args__ = (
        Index("ix_user_overrides_user_field_type", "user_id", "field_id", "override_type"),
    )
