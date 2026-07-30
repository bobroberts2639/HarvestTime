"""Field Notes module — API routes for farmer observations and context."""

from uuid import UUID
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Field, FieldNote

router = APIRouter(prefix="/api/v1/notes", tags=["notes"])


@router.get("/{field_id}")
async def list_notes(
    field_id: UUID,
    season_year: int | None = Query(default=None),
    tag: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List field notes, optionally filtered by season year or tag."""
    result = await db.execute(select(Field).where(Field.id == field_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Field not found")

    query = select(FieldNote).where(FieldNote.field_id == field_id)
    if season_year is not None:
        query = query.where(FieldNote.season_year == season_year)
    query = query.order_by(FieldNote.created_at.desc()).limit(limit)

    result = await db.execute(query)
    notes = result.scalars().all()

    if tag:
        notes = [n for n in notes if tag in (n.tags or [])]

    return {
        "field_id": str(field_id),
        "count": len(notes),
        "notes": [
            {
                "id": str(n.id),
                "content": n.content,
                "photo_url": n.photo_url,
                "tags": n.tags or [],
                "season_year": n.season_year,
                "created_at": n.created_at.isoformat() if n.created_at else None,
            }
            for n in notes
        ],
    }


@router.post("/{field_id}", status_code=201)
async def create_note(
    field_id: UUID,
    user_id: UUID,
    data: dict,
    db: AsyncSession = Depends(get_db),
):
    """Create a new field note."""
    result = await db.execute(select(Field).where(Field.id == field_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Field not found")

    content = data.get("content")
    if not content:
        raise HTTPException(status_code=400, detail="content is required")

    note = FieldNote(
        field_id=field_id,
        user_id=user_id,
        content=content,
        photo_url=data.get("photo_url"),
        tags=data.get("tags", []),
        season_year=data.get("season_year", date.today().year),
    )
    db.add(note)
    await db.flush()

    return {
        "id": str(note.id),
        "field_id": str(field_id),
        "content": note.content,
        "tags": note.tags,
        "season_year": note.season_year,
        "created_at": note.created_at.isoformat() if note.created_at else None,
    }


@router.get("/{field_id}/{note_id}")
async def get_note(field_id: UUID, note_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a specific field note."""
    result = await db.execute(
        select(FieldNote).where(FieldNote.id == note_id, FieldNote.field_id == field_id)
    )
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    return {
        "id": str(note.id),
        "field_id": str(field_id),
        "content": note.content,
        "photo_url": note.photo_url,
        "tags": note.tags or [],
        "season_year": note.season_year,
        "created_at": note.created_at.isoformat() if note.created_at else None,
        "updated_at": note.updated_at.isoformat() if note.updated_at else None,
    }


@router.put("/{field_id}/{note_id}")
async def update_note(field_id: UUID, note_id: UUID, data: dict, db: AsyncSession = Depends(get_db)):
    """Update a field note."""
    result = await db.execute(
        select(FieldNote).where(FieldNote.id == note_id, FieldNote.field_id == field_id)
    )
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    if "content" in data:
        note.content = data["content"]
    if "tags" in data:
        note.tags = data["tags"]
    if "photo_url" in data:
        note.photo_url = data["photo_url"]

    await db.flush()
    return {"id": str(note.id), "field_id": str(field_id), "content": note.content, "tags": note.tags or []}


@router.delete("/{field_id}/{note_id}", status_code=204)
async def delete_note(field_id: UUID, note_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete a field note."""
    result = await db.execute(
        select(FieldNote).where(FieldNote.id == note_id, FieldNote.field_id == field_id)
    )
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    await db.delete(note)
    await db.flush()


@router.get("/search/{field_id}")
async def search_notes(field_id: UUID, q: str = Query(..., min_length=1), db: AsyncSession = Depends(get_db)):
    """Full-text search field notes."""
    result = await db.execute(
        select(FieldNote)
        .where(
            FieldNote.field_id == field_id,
            text("to_tsvector('english', content) @@ plainto_tsquery('english', :query)"),
        )
        .params(query=q)
        .order_by(FieldNote.created_at.desc())
        .limit(20)
    )
    notes = result.scalars().all()
    return {
        "field_id": str(field_id),
        "query": q,
        "count": len(notes),
        "notes": [
            {"id": str(n.id), "content": n.content, "tags": n.tags or [], "season_year": n.season_year}
            for n in notes
        ],
    }
