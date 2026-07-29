"""Pydantic schemas for API request/response validation."""

from datetime import datetime, date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# --- User Schemas ---

class UserCreate(BaseModel):
    email: str
    name: str
    phone: str | None = None
    timezone: str = "UTC"


class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    phone: str | None
    timezone: str
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Farm Schemas ---

class FarmCreate(BaseModel):
    name: str
    latitude: float | None = None
    longitude: float | None = None
    timezone: str | None = None


class FarmResponse(BaseModel):
    id: UUID
    name: str
    timezone: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Field Schemas ---

class FieldCreate(BaseModel):
    name: str
    area_hectares: Decimal | None = None
    # Boundary GeoJSON would be submitted separately


class FieldResponse(BaseModel):
    id: UUID
    name: str
    area_hectares: Decimal | None
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Crop Schemas ---

class CropResponse(BaseModel):
    id: UUID
    name: str
    family: str | None
    growing_season_start: int | None
    growing_season_end: int | None
    base_gdd_temp: Decimal | None

    model_config = {"from_attributes": True}


# --- CropPlanting Schemas ---

class CropPlantingCreate(BaseModel):
    field_id: UUID
    crop_id: UUID
    planted_date: date
    expected_harvest_date: date | None = None
    variety: str | None = None
    seeding_rate: Decimal | None = None


class CropPlantingResponse(BaseModel):
    id: UUID
    field_id: UUID
    crop_id: UUID
    planted_date: date
    expected_harvest_date: date | None
    variety: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Recommendation Schemas ---

class RecommendationResponse(BaseModel):
    id: UUID
    field_id: UUID
    priority: str
    category: str
    title: str
    summary: str
    reasoning: dict | None
    action_items: list
    status: str
    valid_from: date
    valid_until: date
    generated_at: datetime

    model_config = {"from_attributes": True}


class RecommendationFeedbackCreate(BaseModel):
    response: str  # done|skipped|modified|dismissed
    note: str | None = None


# --- Alert Schemas ---

class AlertResponse(BaseModel):
    id: UUID
    field_id: UUID | None
    trigger_type: str
    severity: str
    title: str
    message: str
    triggered_at: datetime
    expires_at: datetime | None
    source: str

    model_config = {"from_attributes": True}


# --- Field Note Schemas ---

class FieldNoteCreate(BaseModel):
    content: str
    tags: list[str] = []
    photo_url: str | None = None


class FieldNoteResponse(BaseModel):
    id: UUID
    field_id: UUID
    content: str
    photo_url: str | None
    tags: list[str]
    season_year: int
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Ownership Schemas ---

class UserPreferencesUpdate(BaseModel):
    units: str | None = None
    language: str | None = None
    organic_mode: bool | None = None
    seasonal_goals: list | None = None
    recommendation_preferences: dict | None = None


class UserPreferencesResponse(BaseModel):
    id: UUID
    units: str
    language: str
    organic_mode: bool
    seasonal_goals: list
    recommendation_preferences: dict

    model_config = {"from_attributes": True}
