"""Recommendation Engine — the heart of Harvest Time.

6-step flow:
1. Rule Generation → crop stage × weather × soil
2. Override Application → UserOverrides take precedence
3. Preference Filtering → UserPreferences shape rankings
4. Feedback Adjustment → >70% skip demotes, >70% done boosts
5. Constraint Checking → CustomEvents block scheduling conflicts
6. Threshold Checking → AlertThreshold personalizes alert triggers
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Field, CropPlanting, Crop, SoilProfile, UserPreferences,
    AlertThreshold, CustomEvent, UserOverride, Recommendation,
    RecommendationFeedback,
)
from app.models.weather import WeatherForecast, GrowingDegreeDay


class RecommendationEngine:
    """Generates weekly recommendations for a field by fusing weather + crop + soil data."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_weekly_advice(self, field_id: UUID) -> list[dict]:
        """Generate prioritized recommendations for a field for this week."""
        # Step 0: Load all context
        field = await self._load_field(field_id)
        if not field:
            return []

        user_id = field.farm.user_id
        plantings = await self._load_active_plantings(field_id)
        weather = await self._load_forecast(field_id, days=7)
        soil = await self._load_soil_profile(field_id)
        preferences = await self._load_preferences(user_id)
        overrides = await self._load_overrides(user_id, field_id)
        custom_events = await self._load_custom_events(user_id)
        feedback_scores = await self._load_feedback_scores(user_id)

        recommendations = []

        for planting in plantings:
            crop = planting.crop
            crop_rules = self._get_crop_rules(crop)

            # Step 1: Generate raw rules
            raw_rules = self._generate_rules(planting, crop_rules, weather, soil)

            # Step 2: Apply overrides
            overridden_rules = self._apply_overrides(raw_rules, overrides)

            # Step 3: Filter by preferences
            filtered_rules = self._filter_by_preferences(overridden_rules, preferences)

            # Step 4: Adjust by feedback scores
            scored_rules = self._adjust_by_feedback(filtered_rules, feedback_scores, crop.id)

            # Step 5: Check scheduling constraints
            constrained_rules = self._check_constraints(scored_rules, custom_events)

            # Step 6: Apply alert thresholds
            final_rules = self._apply_thresholds(constrained_rules, user_id, crop.name)

            recommendations.extend(final_rules)

        # Priority-rank all recommendations
        ranked = self._priority_rank(recommendations)

        # Store in DB
        stored = await self._store_recommendations(field_id, plantings, ranked)

        return stored

    async def _load_field(self, field_id: UUID) -> Field | None:
        result = await self.db.execute(select(Field).where(Field.id == field_id))
        return result.scalar_one_or_none()

    async def _load_active_plantings(self, field_id: UUID) -> list[CropPlanting]:
        result = await self.db.execute(
            select(CropPlanting)
            .where(CropPlanting.field_id == field_id, CropPlanting.status == "growing")
            .where(CropPlanting.crop_id.isnot(None))
        )
        return list(result.scalars().all())

    async def _load_forecast(self, field_id: UUID, days: int) -> list[WeatherForecast]:
        cutoff = date.today() + timedelta(days=days)
        result = await self.db.execute(
            select(WeatherForecast)
            .where(
                WeatherForecast.field_id == field_id,
                WeatherForecast.forecast_date <= cutoff,
                WeatherForecast.forecast_date >= date.today(),
            )
            .order_by(WeatherForecast.forecast_date)
        )
        return list(result.scalars().all())

    async def _load_soil_profile(self, field_id: UUID) -> SoilProfile | None:
        result = await self.db.execute(
            select(SoilProfile).where(
                SoilProfile.field_id == field_id,
                SoilProfile.is_active == True,
            )
        )
        return result.scalar_one_or_none()

    async def _load_preferences(self, user_id: UUID) -> UserPreferences | None:
        result = await self.db.execute(
            select(UserPreferences).where(UserPreferences.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def _load_overrides(self, user_id: UUID, field_id: UUID) -> list[UserOverride]:
        result = await self.db.execute(
            select(UserOverride).where(
                UserOverride.user_id == user_id,
                (UserOverride.field_id == field_id) | (UserOverride.field_id.is_(None)),
            )
        )
        return list(result.scalars().all())

    async def _load_custom_events(self, user_id: UUID) -> list[CustomEvent]:
        today = date.today()
        week_end = today + timedelta(days=7)
        result = await self.db.execute(
            select(CustomEvent).where(
                CustomEvent.user_id == user_id,
                CustomEvent.start_time <= week_end,
            )
        )
        return list(result.scalars().all())

    async def _load_feedback_scores(self, user_id: UUID) -> dict:
        """Load per-crop-category feedback scores (>70% skip demotes, >70% done boosts)."""
        result = await self.db.execute(
            select(
                Recommendation.category,
                RecommendationFeedback.response,
                func.count(RecommendationFeedback.id),
            )
            .join(RecommendationFeedback, RecommendationFeedback.recommendation_id == Recommendation.id)
            .where(RecommendationFeedback.user_id == user_id)
            .group_by(Recommendation.category, RecommendationFeedback.response)
        )

        scores = {}
        for category, response, count in result:
            if category not in scores:
                scores[category] = {"done": 0, "skipped": 0, "total": 0}
            scores[category][response] = count
            scores[category]["total"] += count

        return scores

    def _get_crop_rules(self, crop: Crop) -> list[dict]:
        """Get rule definitions for a crop type."""
        # These would come from a rules database in production
        # For MVP, hardcoded rules per crop
        return [
            {
                "id": "nitrogen_check",
                "category": "fertilization",
                "condition": "gdd_threshold",
                "threshold": 500,
                "action": "Apply nitrogen before next rain",
                "priority": "high",
            },
            {
                "id": "frost_protection",
                "category": "weather",
                "condition": "frost_risk",
                "threshold": 0,
                "action": "Frost protection needed",
                "priority": "critical",
            },
            {
                "id": "irrigation_check",
                "category": "irrigation",
                "condition": "soil_moisture_low",
                "threshold": 30,
                "action": "Schedule irrigation",
                "priority": "medium",
            },
            {
                "id": "harvest_window",
                "category": "harvest",
                "condition": "gdd_reached",
                "threshold": 2500,
                "action": "Check harvest readiness",
                "priority": "high",
            },
        ]

    def _generate_rules(
        self,
        planting: CropPlanting,
        crop_rules: list[dict],
        weather: list[WeatherForecast],
        soil: SoilProfile | None,
    ) -> list[dict]:
        """Step 1: Generate rules based on current conditions."""
        generated = []
        # Simplified rule generation for MVP
        for rule in crop_rules:
            if rule["condition"] == "frost_risk":
                # Check if any forecast day has low temp near threshold
                for day in weather:
                    if day.temperature_low_c and day.temperature_low_c <= rule["threshold"]:
                        generated.append({
                            "rule_id": rule["id"],
                            "category": rule["category"],
                            "title": rule["action"],
                            "summary": f"Temperature expected to drop to {day.temperature_low_c}°C on {day.forecast_date}",
                            "priority": rule["priority"],
                            "reasoning": {
                                "weather_context": f"Forecast low: {day.temperature_low_c}°C on {day.forecast_date}",
                                "rule": rule["id"],
                            },
                        })
                        break

            elif rule["condition"] == "soil_moisture_low" and soil:
                # Check soil moisture (simplified)
                if soil.water_holding_capacity and soil.water_holding_capacity < rule["threshold"]:
                    generated.append({
                        "rule_id": rule["id"],
                        "category": rule["category"],
                        "title": rule["action"],
                        "summary": f"Soil moisture is below optimal ({soil.water_holding_capacity}mm available water)",
                        "priority": rule["priority"],
                        "reasoning": {
                            "soil_context": f"Water holding capacity: {soil.water_holding_capacity}mm",
                            "rule": rule["id"],
                        },
                    })

        return generated

    def _apply_overrides(self, rules: list[dict], overrides: list[UserOverride]) -> list[dict]:
        """Step 2: Apply user overrides — farmer's explicit overrides take precedence."""
        # For MVP, overrides can suppress or modify rules
        override_map = {}
        for o in overrides:
            if o.override_type == "threshold":
                override_map[o.override_value.get("rule_id")] = o.override_value

        result = []
        for rule in rules:
            if rule["rule_id"] in override_map:
                # Apply override (modify threshold, suppress, etc.)
                override = override_map[rule["rule_id"]]
                if override.get("suppress"):
                    continue  # Skip this rule entirely
                rule["priority"] = override.get("priority", rule["priority"])
            result.append(rule)

        return result

    def _filter_by_preferences(self, rules: list[dict], preferences: UserPreferences | None) -> list[dict]:
        """Step 3: Filter by user preferences (organic mode, skip categories)."""
        if not preferences:
            return rules

        filtered = []
        skip_categories = preferences.recommendation_preferences.get("skip_categories", [])

        for rule in rules:
            if rule["category"] in skip_categories:
                continue
            filtered.append(rule)

        return filtered

    def _adjust_by_feedback(self, rules: list[dict], scores: dict, crop_id: UUID) -> list[dict]:
        """Step 4: Adjust priority based on feedback history."""
        for rule in rules:
            cat_scores = scores.get(rule["category"], {})
            total = cat_scores.get("total", 0)
            if total >= 5:  # Need at least 5 data points
                done_rate = cat_scores.get("done", 0) / total
                skip_rate = cat_scores.get("skipped", 0) / total

                if skip_rate > 0.7:
                    # Demote: farmer keeps skipping this category
                    if rule["priority"] == "high":
                        rule["priority"] = "medium"
                    elif rule["priority"] == "medium":
                        rule["priority"] = "low"

                if done_rate > 0.7:
                    # Boost: farmer consistently follows this category
                    if rule["priority"] == "medium":
                        rule["priority"] = "high"

        return rules

    def _check_constraints(self, rules: list[dict], events: list[CustomEvent]) -> list[dict]:
        """Step 5: Check scheduling constraints from custom events."""
        # For MVP, just flag conflicts rather than suppressing
        for rule in rules:
            rule["has_scheduling_conflict"] = False
            # TODO: Check if rule deadline overlaps with any custom event

        return rules

    def _apply_thresholds(self, rules: list[dict], user_id: UUID, crop_name: str) -> list[dict]:
        """Step 6: Apply custom alert thresholds."""
        # For MVP, thresholds are informational
        return rules

    def _priority_rank(self, recommendations: list[dict]) -> list[dict]:
        """Rank recommendations by priority."""
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        return sorted(recommendations, key=lambda r: priority_order.get(r["priority"], 99))

    async def _store_recommendations(
        self,
        field_id: UUID,
        plantings: list[CropPlanting],
        ranked: list[dict],
    ) -> list[dict]:
        """Store recommendations in DB and return formatted results."""
        today = date.today()
        week_end = today + timedelta(days=7)
        now = datetime.utcnow()

        stored = []
        for rec in ranked:
            db_rec = Recommendation(
                field_id=field_id,
                crop_planting_id=plantings[0].id if plantings else None,
                generated_at=now,
                valid_from=today,
                valid_until=week_end,
                priority=rec["priority"],
                category=rec["category"],
                title=rec["title"],
                summary=rec["summary"],
                reasoning=rec.get("reasoning"),
                action_items=[],
                status="active",
            )
            self.db.add(db_rec)
            await self.db.flush()

            stored.append({
                "id": str(db_rec.id),
                "field_id": str(field_id),
                "priority": rec["priority"],
                "category": rec["category"],
                "title": rec["title"],
                "summary": rec["summary"],
                "valid_from": str(today),
                "valid_until": str(week_end),
            })

        return stored
