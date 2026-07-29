"""Recommendation and Alert module entities."""

import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, Numeric, DateTime, Date, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class Recommendation(Base):
    """Recommendation — core output of the weekly advisor."""
    __tablename__ = "recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_id = Column(UUID(as_uuid=True), ForeignKey("fields.id"), nullable=False, index=True)
    crop_planting_id = Column(UUID(as_uuid=True), ForeignKey("crop_plantings.id"), nullable=True)
    generated_at = Column(DateTime(timezone=True), nullable=False)
    valid_from = Column(Date, nullable=False)
    valid_until = Column(Date, nullable=False)
    priority = Column(String(10), nullable=False)  # critical|high|medium|low
    category = Column(String(20), nullable=False)  # irrigation|fertilization|pest|planting|harvest|weather|soil|general
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    reasoning = Column(JSONB, nullable=True)  # {weather_context, soil_context, crop_context, rules_applied}
    action_items = Column(JSONB, default=list, nullable=False)  # [{task, deadline, estimated_effort}]
    status = Column(String(20), default="active", nullable=False)  # active|acknowledged|dismissed|completed

    # Relationships
    field = relationship("Field", back_populates="recommendations")
    crop_planting = relationship("CropPlanting", back_populates="recommendations")
    feedback_entries = relationship("RecommendationFeedback", back_populates="recommendation", lazy="noload")

    __table_args__ = (
        Index("ix_recommendations_field_status", "field_id", "status"),
        Index("ix_recommendations_field_valid", "field_id", "valid_until"),
    )


class RecommendationFeedback(Base):
    """RecommendationFeedback — farmer's response to a recommendation."""
    __tablename__ = "recommendation_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recommendation_id = Column(UUID(as_uuid=True), ForeignKey("recommendations.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    response = Column(String(10), nullable=False)  # done|skipped|modified|dismissed
    note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    recommendation = relationship("Recommendation", back_populates="feedback_entries")


class Alert(Base):
    """Alert — real-time weather and system alerts."""
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_id = Column(UUID(as_uuid=True), ForeignKey("fields.id"), nullable=True, index=True)
    trigger_type = Column(String(20), nullable=False)  # frost|heat|drought|flood|wind|pest|disease
    severity = Column(String(10), nullable=False)  # warning|watch|advisory
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    triggered_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    source = Column(String(20), default="weather_api", nullable=False)  # weather_api|user_defined|system
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    field = relationship("Field", back_populates="alerts")

    __table_args__ = (
        Index("ix_alerts_field_time", "field_id", "triggered_at"),
        Index("ix_alerts_active", "expires_at"),
    )


class SeasonalPlan(Base):
    """SeasonalPlan — long-range planning per field per season."""
    __tablename__ = "seasonal_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_id = Column(UUID(as_uuid=True), ForeignKey("fields.id"), nullable=False, index=True)
    crop_id = Column(UUID(as_uuid=True), ForeignKey("crops.id"), nullable=True)
    season = Column(String(10), nullable=False)  # spring|summer|fall|winter
    year = Column(Integer, nullable=False)
    planned_activities = Column(JSONB, default=list, nullable=False)
    notes = Column(Text, nullable=True)

    __table_args__ = (
        Index("ix_seasonal_plans_field_season", "field_id", "season", "year", unique=True),
    )
