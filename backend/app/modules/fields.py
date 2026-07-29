"""Fields module — API routes for farm and field management."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User, Farm, Field
from app.schemas import FarmCreate, FarmResponse, FieldCreate, FieldResponse

router = APIRouter(prefix="/api/v1/fields", tags=["fields"])


@router.get("/", response_model=list[FarmResponse])
async def list_farms(user_id: UUID, db: AsyncSession = Depends(get_db)):
    """List all farms for a user."""
    result = await db.execute(
        select(Farm).where(Farm.user_id == user_id).order_by(Farm.created_at.desc())
    )
    return result.scalars().all()


@router.post("/", response_model=FarmResponse, status_code=201)
async def create_farm(user_id: UUID, data: FarmCreate, db: AsyncSession = Depends(get_db)):
    """Create a new farm."""
    farm = Farm(
        user_id=user_id,
        name=data.name,
        timezone=data.timezone,
    )
    # If lat/lng provided, create geography point
    if data.latitude is not None and data.longitude is not None:
        from geoalchemy2.elements import WKTElement
        farm.location = WKTElement(f"POINT({data.longitude} {data.latitude})", srid=4326)

    db.add(farm)
    await db.flush()
    return farm


@router.get("/{farm_id}", response_model=FarmResponse)
async def get_farm(farm_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a specific farm."""
    result = await db.execute(select(Farm).where(Farm.id == farm_id))
    farm = result.scalar_one_or_none()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    return farm


# --- Field endpoints ---


@router.get("/{farm_id}/fields", response_model=list[FieldResponse])
async def list_fields(farm_id: UUID, db: AsyncSession = Depends(get_db)):
    """List all fields for a farm."""
    result = await db.execute(
        select(Field).where(Field.farm_id == farm_id).order_by(Field.created_at.desc())
    )
    return result.scalars().all()


@router.post("/{farm_id}/fields", response_model=FieldResponse, status_code=201)
async def create_field(farm_id: UUID, data: FieldCreate, db: AsyncSession = Depends(get_db)):
    """Create a new field within a farm."""
    # Verify farm exists
    result = await db.execute(select(Farm).where(Farm.id == farm_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Farm not found")

    field = Field(
        farm_id=farm_id,
        name=data.name,
        area_hectares=data.area_hectares,
    )
    db.add(field)
    await db.flush()
    return field


@router.get("/{farm_id}/fields/{field_id}", response_model=FieldResponse)
async def get_field(farm_id: UUID, field_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a specific field."""
    result = await db.execute(
        select(Field).where(Field.id == field_id, Field.farm_id == farm_id)
    )
    field = result.scalar_one_or_none()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    return field
