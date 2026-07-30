"""initial schema — all core, weather, recommendation, and ownership tables

Revision ID: 001_initial
Revises: 
Create Date: 2026-07-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from geoalchemy2 import Geography

revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ============================================================
    # CORE ENTITIES
    # ============================================================

    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String, unique=True, nullable=False),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('phone', sa.String, nullable=True),
        sa.Column('timezone', sa.String, nullable=False, server_default='UTC'),
        sa.Column('preferences', JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    op.create_table(
        'farms',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('location', Geography(geometry_type='POINT', srid=4326), nullable=True),
        sa.Column('timezone', sa.String, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_farms_user_id', 'farms', ['user_id'])

    op.create_table(
        'fields',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('farm_id', UUID(as_uuid=True), sa.ForeignKey('farms.id'), nullable=False),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('area_hectares', sa.Numeric(10, 2), nullable=True),
        sa.Column('boundary', Geography(geometry_type='POLYGON', srid=4326), nullable=True),
        sa.Column('metadata', JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_fields_farm_id', 'fields', ['farm_id'])

    op.create_table(
        'crops',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String, nullable=False, unique=True),
        sa.Column('family', sa.String, nullable=True),
        sa.Column('growing_season_start', sa.Integer, nullable=True),
        sa.Column('growing_season_end', sa.Integer, nullable=True),
        sa.Column('base_gdd_temp', sa.Numeric(5, 2), nullable=True),
        sa.Column('growth_stages', JSONB, nullable=True),
        sa.Column('water_needs', JSONB, nullable=True),
        sa.Column('temp_range', JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        'crop_plantings',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('field_id', UUID(as_uuid=True), sa.ForeignKey('fields.id'), nullable=False),
        sa.Column('crop_id', UUID(as_uuid=True), sa.ForeignKey('crops.id'), nullable=False),
        sa.Column('planted_date', sa.Date, nullable=False),
        sa.Column('expected_harvest_date', sa.Date, nullable=True),
        sa.Column('actual_harvest_date', sa.Date, nullable=True),
        sa.Column('variety', sa.String, nullable=True),
        sa.Column('seeding_rate', sa.Numeric(10, 2), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='planted'),
        sa.Column('metadata', JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_crop_plantings_field_id', 'crop_plantings', ['field_id'])
    op.create_index('ix_crop_plantings_crop_id', 'crop_plantings', ['crop_id'])
    op.create_index('ix_crop_plantings_field_status', 'crop_plantings', ['field_id', 'status'])

    op.create_table(
        'soil_profiles',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('field_id', UUID(as_uuid=True), sa.ForeignKey('fields.id'), nullable=False),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('soil_type', sa.String(20), nullable=True),
        sa.Column('ph', sa.Numeric(3, 1), nullable=True),
        sa.Column('organic_matter_pct', sa.Numeric(5, 2), nullable=True),
        sa.Column('nitrogen_ppm', sa.Numeric, nullable=True),
        sa.Column('phosphorus_ppm', sa.Numeric, nullable=True),
        sa.Column('potassium_ppm', sa.Numeric, nullable=True),
        sa.Column('drainage_class', sa.String(20), nullable=True),
        sa.Column('water_holding_capacity', sa.Numeric, nullable=True),
        sa.Column('cec', sa.Numeric, nullable=True),
        sa.Column('last_tested_date', sa.Date, nullable=True),
        sa.Column('raw_lab_results', JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_soil_profiles_field_id', 'soil_profiles', ['field_id'])

    # ============================================================
    # OWNERSHIP & PERSONALIZATION ENTITIES
    # ============================================================

    op.create_table(
        'user_preferences',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), unique=True, nullable=False),
        sa.Column('units', sa.String(10), nullable=False, server_default='metric'),
        sa.Column('language', sa.String(10), nullable=False, server_default='en'),
        sa.Column('organic_mode', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('seasonal_goals', JSONB, nullable=False, server_default='[]'),
        sa.Column('recommendation_preferences', JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_user_preferences_user_id', 'user_preferences', ['user_id'], unique=True)

    op.create_table(
        'alert_thresholds',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('crop_type', sa.String, nullable=True),
        sa.Column('alert_type', sa.String(20), nullable=False),
        sa.Column('threshold_value', sa.Numeric, nullable=False),
        sa.Column('unit', sa.String(10), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_alert_thresholds_user_id', 'alert_thresholds', ['user_id'])
    op.create_index('ix_alert_thresholds_user_crop_type', 'alert_thresholds', ['user_id', 'crop_type', 'alert_type'])

    op.create_table(
        'field_notes',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('field_id', UUID(as_uuid=True), sa.ForeignKey('fields.id'), nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('photo_url', sa.String, nullable=True),
        sa.Column('tags', ARRAY(sa.String), nullable=False, server_default='{}'),
        sa.Column('season_year', sa.Integer, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_field_notes_field_id', 'field_notes', ['field_id'])
    op.create_index('ix_field_notes_user_id', 'field_notes', ['user_id'])
    op.create_index('ix_field_notes_field_season', 'field_notes', ['field_id', 'season_year'])
    op.execute("CREATE INDEX ix_field_notes_tags ON field_notes USING gin (tags)")
    op.execute("CREATE INDEX ix_field_notes_content_fts ON field_notes USING gin (to_tsvector('english', content))")

    op.create_table(
        'season_journals',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('season_year', sa.Integer, nullable=False),
        sa.Column('reflections', JSONB, nullable=False, server_default='{}'),
        sa.Column('stats', JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_season_journals_user_id', 'season_journals', ['user_id'])
    op.create_index('ix_season_journals_user_year', 'season_journals', ['user_id', 'season_year'], unique=True)

    op.create_table(
        'custom_events',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('field_id', UUID(as_uuid=True), sa.ForeignKey('fields.id'), nullable=True),
        sa.Column('event_type', sa.String(20), nullable=False),
        sa.Column('title', sa.String, nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('recurrence', JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_custom_events_user_id', 'custom_events', ['user_id'])
    op.create_index('ix_custom_events_field_id', 'custom_events', ['field_id'])
    op.create_index('ix_custom_events_user_time', 'custom_events', ['user_id', 'start_time', 'end_time'])

    op.create_table(
        'user_overrides',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('field_id', UUID(as_uuid=True), sa.ForeignKey('fields.id'), nullable=True),
        sa.Column('override_type', sa.String(20), nullable=False),
        sa.Column('override_value', JSONB, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_user_overrides_user_id', 'user_overrides', ['user_id'])
    op.create_index('ix_user_overrides_field_id', 'user_overrides', ['field_id'])
    op.create_index('ix_user_overrides_user_field_type', 'user_overrides', ['user_id', 'field_id', 'override_type'])

    # ============================================================
    # WEATHER MODULE
    # ============================================================

    op.create_table(
        'weather_stations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String, nullable=True),
        sa.Column('location', Geography(geometry_type='POINT', srid=4326), nullable=True),
        sa.Column('provider', sa.String, nullable=False),
        sa.Column('external_id', sa.String, nullable=False),
    )

    op.create_table(
        'weather_observations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('field_id', UUID(as_uuid=True), sa.ForeignKey('fields.id'), nullable=False),
        sa.Column('station_id', UUID(as_uuid=True), sa.ForeignKey('weather_stations.id'), nullable=True),
        sa.Column('observed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('temperature_c', sa.Numeric(5, 2), nullable=True),
        sa.Column('humidity_pct', sa.Numeric(5, 2), nullable=True),
        sa.Column('precipitation_mm', sa.Numeric(8, 2), nullable=True),
        sa.Column('wind_speed_kmh', sa.Numeric(6, 2), nullable=True),
        sa.Column('wind_direction_deg', sa.Integer, nullable=True),
        sa.Column('solar_radiation_wm2', sa.Numeric(7, 2), nullable=True),
        sa.Column('soil_temperature_c', sa.Numeric(5, 2), nullable=True),
        sa.Column('raw_data', JSONB, nullable=True),
    )
    op.create_index('ix_weather_observations_field_id', 'weather_observations', ['field_id'])
    op.create_index('ix_weather_obs_field_date', 'weather_observations', ['field_id', 'observed_at'])

    op.create_table(
        'weather_forecasts',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('field_id', UUID(as_uuid=True), sa.ForeignKey('fields.id'), nullable=False),
        sa.Column('forecast_date', sa.Date, nullable=False),
        sa.Column('forecast_hour', sa.Integer, nullable=True),
        sa.Column('temperature_high_c', sa.Numeric(5, 2), nullable=True),
        sa.Column('temperature_low_c', sa.Numeric(5, 2), nullable=True),
        sa.Column('precipitation_probability_pct', sa.Numeric(5, 2), nullable=True),
        sa.Column('precipitation_mm', sa.Numeric(8, 2), nullable=True),
        sa.Column('humidity_pct', sa.Numeric(5, 2), nullable=True),
        sa.Column('wind_speed_kmh', sa.Numeric(6, 2), nullable=True),
        sa.Column('solar_radiation_wm2', sa.Numeric(7, 2), nullable=True),
        sa.Column('source', sa.String, nullable=False),
        sa.Column('fetched_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('raw_data', JSONB, nullable=True),
    )
    op.create_index('ix_weather_forecasts_field_id', 'weather_forecasts', ['field_id'])
    op.create_index('ix_weather_forecast_field_date', 'weather_forecasts', ['field_id', 'forecast_date'])

    op.create_table(
        'growing_degree_days',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('field_id', UUID(as_uuid=True), sa.ForeignKey('fields.id'), nullable=False),
        sa.Column('crop_planting_id', UUID(as_uuid=True), sa.ForeignKey('crop_plantings.id'), nullable=False),
        sa.Column('date', sa.Date, nullable=False),
        sa.Column('max_temp_c', sa.Numeric(5, 2), nullable=False),
        sa.Column('min_temp_c', sa.Numeric(5, 2), nullable=False),
        sa.Column('gdd', sa.Numeric(6, 2), nullable=False),
        sa.Column('cumulative_gdd', sa.Numeric(8, 2), nullable=False),
    )
    op.create_index('ix_growing_degree_days_field_id', 'growing_degree_days', ['field_id'])
    op.create_index('ix_gdd_planting_date', 'growing_degree_days', ['crop_planting_id', 'date'])

    # ============================================================
    # RECOMMENDATION & ALERT MODULE
    # ============================================================

    op.create_table(
        'recommendations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('field_id', UUID(as_uuid=True), sa.ForeignKey('fields.id'), nullable=False),
        sa.Column('crop_planting_id', UUID(as_uuid=True), sa.ForeignKey('crop_plantings.id'), nullable=True),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('valid_from', sa.Date, nullable=False),
        sa.Column('valid_until', sa.Date, nullable=False),
        sa.Column('priority', sa.String(10), nullable=False),
        sa.Column('category', sa.String(20), nullable=False),
        sa.Column('title', sa.String, nullable=False),
        sa.Column('summary', sa.Text, nullable=False),
        sa.Column('reasoning', JSONB, nullable=True),
        sa.Column('action_items', JSONB, nullable=False, server_default='[]'),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_recommendations_field_id', 'recommendations', ['field_id'])
    op.create_index('ix_recommendations_field_status', 'recommendations', ['field_id', 'status'])
    op.create_index('ix_recommendations_field_valid', 'recommendations', ['field_id', 'valid_until'])

    op.create_table(
        'recommendation_feedback',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('recommendation_id', UUID(as_uuid=True), sa.ForeignKey('recommendations.id'), nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('response', sa.String(10), nullable=False),
        sa.Column('note', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_recommendation_feedback_recommendation_id', 'recommendation_feedback', ['recommendation_id'])
    op.create_index('ix_recommendation_feedback_user_id', 'recommendation_feedback', ['user_id'])

    op.create_table(
        'alerts',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('field_id', UUID(as_uuid=True), sa.ForeignKey('fields.id'), nullable=True),
        sa.Column('trigger_type', sa.String(20), nullable=False),
        sa.Column('severity', sa.String(10), nullable=False),
        sa.Column('title', sa.String, nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('triggered_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('source', sa.String(20), nullable=False, server_default='weather_api'),
        sa.Column('acknowledged_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_alerts_field_id', 'alerts', ['field_id'])
    op.create_index('ix_alerts_field_time', 'alerts', ['field_id', 'triggered_at'])
    op.create_index('ix_alerts_active', 'alerts', ['expires_at'])

    op.create_table(
        'seasonal_plans',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('field_id', UUID(as_uuid=True), sa.ForeignKey('fields.id'), nullable=False),
        sa.Column('crop_id', UUID(as_uuid=True), sa.ForeignKey('crops.id'), nullable=True),
        sa.Column('season', sa.String(10), nullable=False),
        sa.Column('year', sa.Integer, nullable=False),
        sa.Column('planned_activities', JSONB, nullable=False, server_default='[]'),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_seasonal_plans_field_id', 'seasonal_plans', ['field_id'])
    op.create_index('ix_seasonal_plans_field_season', 'seasonal_plans', ['field_id', 'season', 'year'], unique=True)


def downgrade() -> None:
    op.drop_table('seasonal_plans')
    op.drop_table('alerts')
    op.drop_table('recommendation_feedback')
    op.drop_table('recommendations')
    op.drop_table('growing_degree_days')
    op.drop_table('weather_forecasts')
    op.drop_table('weather_observations')
    op.drop_table('weather_stations')
    op.drop_table('user_overrides')
    op.drop_table('custom_events')
    op.drop_table('season_journals')
    op.drop_table('field_notes')
    op.drop_table('alert_thresholds')
    op.drop_table('user_preferences')
    op.drop_table('soil_profiles')
    op.drop_table('crop_plantings')
    op.drop_table('crops')
    op.drop_table('fields')
    op.drop_table('farms')
    op.drop_table('users')
