"""Recommendations module — API routes for weekly advice and feedback."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Recommendation, RecommendationFeedback
from app.modules.recommendation_engine import RecommendationEngine
from app.schemas import RecommendationFeedbackCreate

router = APIRouter(prefix="/api/v1/recommendations", tags=["recommendations"])


@router.post("/{field_id}/generate")
async def generate_weekly_advice(field_id: UUID, db: AsyncSession = Depends(get_db)):
    """Generate weekly recommendations for a field."""
    engine = RecommendationEngine(db)
    recommendations = await engine.generate_weekly_advice(field_id)
    return {"field_id": str(field_id), "count": len(recommendations), "recommendations": recommendations}


@router.get("/{field_id}/active")
async def get_active_recommendations(field_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get active recommendations for a field."""
    result = await db.execute(
        select(Recommendation)
        .where(Recommendation.field_id == field_id, Recommendation.status == "active")
        .order_by(Recommendation.created_at.desc())
    )
    recs = result.scalars().all()

    return {
        "field_id": str(field_id),
        "count": len(recs),
        "recommendations": [
            {
                "id": str(r.id),
                "priority": r.priority,
                "category": r.category,
                "title": r.title,
                "summary": r.summary,
                "reasoning": r.reasoning,
                "action_items": r.action_items or [],
                "valid_from": str(r.valid_from),
                "valid_until": str(r.valid_until),
                "generated_at": r.generated_at.isoformat() if r.generated_at else None,
            }
            for r in recs
        ],
    }


@router.get("/{field_id}/all")
async def get_all_recommendations(
    field_id: UUID,
    status: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Get all recommendations for a field, optionally filtered by status."""
    query = select(Recommendation).where(Recommendation.field_id == field_id)
    if status:
        query = query.where(Recommendation.status == status)
    query = query.order_by(Recommendation.generated_at.desc())

    result = await db.execute(query)
    recs = result.scalars().all()

    return {
        "field_id": str(field_id),
        "count": len(recs),
        "recommendations": [
            {
                "id": str(r.id),
                "priority": r.priority,
                "category": r.category,
                "title": r.title,
                "summary": r.summary,
                "status": r.status,
                "valid_from": str(r.valid_from),
                "valid_until": str(r.valid_until),
                "generated_at": r.generated_at.isoformat() if r.generated_at else None,
            }
            for r in recs
        ],
    }


@router.post("/{recommendation_id}/feedback", status_code=201)
async def submit_feedback(
    recommendation_id: UUID,
    user_id: UUID,
    data: RecommendationFeedbackCreate,
    db: AsyncSession = Depends(get_db),
):
    """Submit feedback on a recommendation (done/skipped/modified/dismissed)."""
    valid_responses = {"done", "skipped", "modified", "dismissed"}
    if data.response not in valid_responses:
        raise HTTPException(status_code=400, detail=f"Invalid response. Must be one of: {valid_responses}")

    result = await db.execute(select(Recommendation).where(Recommendation.id == recommendation_id))
    rec = result.scalar_one_or_none()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    feedback = RecommendationFeedback(
        recommendation_id=recommendation_id,
        user_id=user_id,
        response=data.response,
        note=data.note,
    )
    db.add(feedback)

    if data.response == "done":
        rec.status = "completed"
    elif data.response == "dismissed":
        rec.status = "dismissed"

    await db.flush()

    return {
        "id": str(feedback.id),
        "recommendation_id": str(recommendation_id),
        "response": feedback.response,
        "note": feedback.note,
        "created_at": feedback.created_at.isoformat() if feedback.created_at else None,
    }


@router.patch("/{recommendation_id}/status")
async def update_recommendation_status(
    recommendation_id: UUID,
    status: str,
    db: AsyncSession = Depends(get_db),
):
    """Update recommendation status (acknowledge, dismiss, complete)."""
    valid_statuses = {"active", "acknowledged", "dismissed", "completed"}
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")

    result = await db.execute(select(Recommendation).where(Recommendation.id == recommendation_id))
    rec = result.scalar_one_or_none()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    rec.status = status
    await db.flush()
    return {"id": str(rec.id), "status": rec.status}
