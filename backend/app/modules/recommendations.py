"""Recommendations module — API routes for weekly advice."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.modules.recommendation_engine import RecommendationEngine

router = APIRouter(prefix="/api/v1/recommendations", tags=["recommendations"])


@router.post("/{field_id}/generate")
async def generate_weekly_advice(
    field_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Generate weekly recommendations for a field."""
    engine = RecommendationEngine(db)
    recommendations = await engine.generate_weekly_advice(field_id)

    return {
        "field_id": str(field_id),
        "count": len(recommendations),
        "recommendations": recommendations,
    }


@router.get("/{field_id}/active")
async def get_active_recommendations(
    field_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get active recommendations for a field."""
    from sqlalchemy import select
    from app.models import Recommendation

    result = await db.execute(
        select(Recommendation)
        .where(Recommendation.field_id == field_id, Recommendation.status == "active")
        .order_by(Recommendation.generated_at.desc())
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
                "valid_from": str(r.valid_from),
                "valid_until": str(r.valid_until),
            }
            for r in recs
        ],
    }
