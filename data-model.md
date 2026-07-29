# Harvest Time — Data Model

## Architecture Principle

One PostgreSQL database, one schema. Entities organized into **Core** (shared by all modules) and **Module** (domain-specific) groups. Module tables reference core entities via foreign keys. No cross-module foreign keys — modules are decoupled through the core layer.

---

## Core Entities

### User
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| email | VARCHAR unique | |
| name | VARCHAR | |
| timezone | VARCHAR | Default: UTC |
| preferences | JSONB | Notification prefs, units, etc. |
| created_at, updated_at | TIMESTAMPTZ | |

### Farm
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| user_id | UUID FK → User | |
| name | VARCHAR | |
| location | GEOGRAPHY(Point) | Lat/lng + elevation |
| timezone | VARCHAR | Inherited from User, overridable |
| created_at, updated_at | TIMESTAMPTZ | |

### Field
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| farm_id | UUID FK → Farm | |
| name | VARCHAR | |
| area_hectares | DECIMAL | |
| boundary | GEOGRAPHY(Polygon) | GeoJSON polygon for spatial queries |
| metadata | JSONB | Extension point for future modules |
| created_at, updated_at | TIMESTAMPTZ | |

### Crop (Reference/Lookup)
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| name | VARCHAR | "Winter Wheat", "Corn" |
| family | VARCHAR | Poaceae, Fabaceae, etc. |
| growing_season_start | INT | Month (1-12) |
| growing_season_end | INT | Month (1-12) |
| base_gdd_temp | DECIMAL | Base temp for GDD calculation |
| growth_stages | JSONB | Array of {name, min_gdd, max_gdd, typical_duration_days} |
| water_needs | JSONB | {mm_per_day_avg, critical_periods: [...]} |
| temp_range | JSONB | {min_germination, max_germination, min_growth, max_growth} |
| created_at | TIMESTAMPTZ | |

### CropPlanting (Active Season Instance)
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| field_id | UUID FK → Field | |
| crop_id | UUID FK → Crop | |
| planted_date | DATE | |
| expected_harvest_date | DATE | |
| actual_harvest_date | DATE nullable | |
| variety | VARCHAR | Specific cultivar |
| seeding_rate | DECIMAL | Seeds per hectare |
| status | VARCHAR enum | planted | growing | harvested | failed |
| metadata | JSONB | Module-specific extension |
| created_at, updated_at | TIMESTAMPTZ | |

### SoilProfile
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| field_id | UUID FK → Field | One active profile per field |
| soil_type | VARCHAR | clay | sandy | loam | silt | peat | chalk |
| ph | DECIMAL(3,1) | |
| organic_matter_pct | DECIMAL(5,2) | |
| nitrogen_ppm | DECIMAL | |
| phosphorus_ppm | DECIMAL | |
| potassium_ppm | DECIMAL | |
| drainage_class | VARCHAR | poor | moderate | well | excessive |
| water_holding_capacity | DECIMAL | mm available water |
| cec | DECIMAL | Cation exchange capacity |
| last_tested_date | DATE | |
| raw_lab_results | JSONB | Arbitrary lab data from soil tests |
| created_at, updated_at | TIMESTAMPTZ | |

---

## Ownership & Personalization Entities

### UserPreferences
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| user_id | UUID FK → User | |
| units | VARCHAR | metric | imperial |
| language | VARCHAR | Default: en |
| organic_mode | BOOLEAN | Swaps synthetic recs for OMRI-listed alternatives |
| seasonal_goals | JSONB | Array of goals that shape recommendations |
| recommendation_preferences | JSONB | Skip categories, notification preferences |
| created_at, updated_at | TIMESTAMPTZ | |

### AlertThreshold
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| user_id | UUID FK → User | |
| crop_type | VARCHAR nullable | null = global default |
| alert_type | VARCHAR | frost | heat | drought | flood | wind |
| threshold_value | DECIMAL | Custom threshold (e.g., 28°F for frost) |
| unit | VARCHAR | |
| created_at, updated_at | TIMESTAMPTZ | |

### FieldNotes
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| field_id | UUID FK → Field | |
| user_id | UUID FK → User | |
| content | TEXT | |
| photo_url | VARCHAR nullable | |
| tags | TEXT[] | GIN-indexed for search |
| season_year | INT | |
| created_at, updated_at | TIMESTAMPTZ | |

### SeasonJournal
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| user_id | UUID FK → User | |
| season_year | INT | |
| reflections | JSONB | {went_well, differently, biggest_surprise, app_help} |
| stats | JSONB | {recommendations_completed, notes_captured, weather_summary} |
| created_at, updated_at | TIMESTAMPTZ | |

### CustomEvents
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| user_id | UUID FK → User | |
| field_id | UUID FK → Field nullable | null = farm-wide event |
| event_type | VARCHAR | labor | equipment | contract | market | custom |
| title | VARCHAR | |
| start_time | TIMESTAMPTZ | |
| end_time | TIMESTAMPTZ | |
| recurrence | JSONB nullable | For repeating events |
| created_at, updated_at | TIMESTAMPTZ | |

### RecommendationFeedback
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| recommendation_id | UUID FK → Recommendation | |
| user_id | UUID FK → User | |
| response | VARCHAR | done | skipped | modified | dismissed |
| note | TEXT nullable | Custom reason or comment |
| created_at | TIMESTAMPTZ | |

### UserOverrides
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| user_id | UUID FK → User | |
| field_id | UUID FK → Field nullable | null = global override |
| override_type | VARCHAR | growth_stage | irrigation | threshold | schedule |
| override_value | JSONB | Varies by type |
| created_at, updated_at | TIMESTAMPTZ | |

---

## Module Entities

### Weather Module

**WeatherStation**
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| name | VARCHAR | |
| location | GEOGRAPHY(Point) | |
| provider | VARCHAR | openweathermap | nws | visualcrossing |
| external_id | VARCHAR | Provider's station ID |

**WeatherObservation** (Historical/actual)
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| field_id | UUID FK → Field | Denormalized for query speed |
| station_id | UUID FK → WeatherStation | |
| observed_at | TIMESTAMPTZ | |
| temperature_c | DECIMAL | |
| humidity_pct | DECIMAL | |
| precipitation_mm | DECIMAL | |
| wind_speed_kmh | DECIMAL | |
| wind_direction_deg | INT | |
| solar_radiation_wm2 | DECIMAL | |
| soil_temperature_c | DECIMAL nullable | |
| raw_data | JSONB | Full API response for debugging |

**WeatherForecast**
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| field_id | UUID FK → Field | |
| forecast_date | DATE | |
| forecast_hour | INT nullable | null = daily aggregate |
| temperature_high_c | DECIMAL | |
| temperature_low_c | DECIMAL | |
| precipitation_probability_pct | DECIMAL | |
| precipitation_mm | DECIMAL | |
| humidity_pct | DECIMAL | |
| wind_speed_kmh | DECIMAL | |
| solar_radiation_wm2 | DECIMAL | |
| source | VARCHAR | API source |
| fetched_at | TIMESTAMPTZ | |
| raw_data | JSONB | |

**GrowingDegreeDay** (Computed daily)
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| field_id | UUID FK → Field | |
| crop_planting_id | UUID FK → CropPlanting | |
| date | DATE | |
| max_temp_c, min_temp_c | DECIMAL | |
| gdd | DECIMAL | Daily GDD |
| cumulative_gdd | DECIMAL | Running total since planting |

### Recommendation Module

**Recommendation**
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| field_id | UUID FK → Field | |
| crop_planting_id | UUID FK → CropPlanting nullable | |
| generated_at | TIMESTAMPTZ | |
| valid_from | DATE | |
| valid_until | DATE | |
| priority | VARCHAR enum | critical | high | medium | low |
| category | VARCHAR enum | irrigation | fertilization | pest | planting | harvest | weather | soil | general |
| title | VARCHAR | Short action label |
| summary | TEXT | One-paragraph explanation |
| reasoning | JSONB | {weather_context, soil_context, crop_context, rules_applied} |
| action_items | JSONB | Array of {task, deadline, estimated_effort} |
| status | VARCHAR enum | active | acknowledged | dismissed | completed |
| created_at, updated_at | TIMESTAMPTZ | |

### Alert Module

**Alert**
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| field_id | UUID FK → Field nullable | null = farm-wide |
| trigger_type | VARCHAR enum | frost | heat | drought | flood | wind | pest | disease |
| severity | VARCHAR enum | warning | watch | advisory |
| title | VARCHAR | |
| message | TEXT | |
| triggered_at | TIMESTAMPTZ | |
| expires_at | TIMESTAMPTZ | |
| source | VARCHAR | weather_api | user_defined | system |
| acknowledged_at | TIMESTAMPTZ nullable | |
| created_at | TIMESTAMPTZ | |

### Seasonal Planning Module

**SeasonalPlan**
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| field_id | UUID FK → Field | |
| crop_id | UUID FK → Crop nullable | |
| season | VARCHAR enum | spring | summer | fall | winter |
| year | INT | |
| planned_activities | JSONB | Array of {date_range, activity_type, description, priority, status} |
| notes | TEXT | |
| created_at, updated_at | TIMESTAMPTZ | |

---

## Relationships

```
User 1──N Farm
Farm 1──N Field
Field 1──N SoilProfile (1 active + history)
Field 1──N CropPlanting
Crop 1──N CropPlanting
CropPlanting 1──N GrowingDegreeDay
CropPlanting 1──N Recommendation (nullable FK)
Field 1──N Recommendation
Field 1──N Alert (nullable FK)
Field 1──N WeatherObservation (denormalized)
Field 1──N WeatherForecast
WeatherStation 1──N WeatherObservation
Field 1──N SeasonalPlan (unique on field+season+year)
Field 1──N FieldNotes
Field 1──N CustomEvents (nullable)
User 1──N UserPreferences
User 1──N AlertThreshold
User 1──N SeasonJournal
User 1──N UserOverrides
Recommendation 1──N RecommendationFeedback
```

---

## Recommendation Engine — 6-Step Query Flow

```
1. Rule Generation → crop stage × weather × soil
2. Override Application → UserOverrides take precedence over system defaults
3. Preference Filtering → UserPreferences shape rankings (organic mode, goals)
4. Feedback Adjustment → >70% skip demotes category, >70% done boosts
5. Constraint Checking → CustomEvents block scheduling conflicts
6. Threshold Checking → AlertThreshold personalizes alert triggers
```

---

## Key Indexes

- `crop_plantings(field_id, status)` — filter active plantings per field
- `growing_degree_days(crop_planting_id, date)` — cumulative GDD lookup
- `weather_observations(field_id, observed_at)` — time-range weather queries
- `weather_forecasts(field_id, forecast_date)` — forecast lookups
- `recommendations(field_id, status, valid_until)` — active recommendations per field
- `alerts(field_id, triggered_at, expires_at)` — live alerts
- `field_notes(field_id, created_at)` — notes timeline
- `field_notes USING gin(tags)` — tag search
- `field_notes USING gin(to_tsvector('english', content))` — full-text search
- `recommendation_feedback(recommendation_id)` — feedback lookup
- `custom_events(user_id, start_time, end_time)` — calendar conflict checks

---

## Schema Evolution

- **Additive-only in v1** — new modules only add tables and nullable columns
- **JSONB for rapid iteration** — prototype new module data in metadata columns
- **Soft deletes** — never hard-delete fields with active plantings
- **Time-series partitioning** — WeatherObservation and GrowingDegreeDay partitioned by month/year from day one
- **Feature flags** — gate new modules, incomplete modules don't create empty tables

### Migration Timeline
- **v0.1** — Core tables: User, Farm, Field, Crop, CropPlanting, SoilProfile
- **v0.2** — Weather module: WeatherStation, WeatherObservation, WeatherForecast, GrowingDegreeDay
- **v0.3** — Recommendation + Alert modules
- **v0.4** — Ownership layer: UserPreferences, AlertThreshold, FieldNotes, RecommendationFeedback, UserOverrides
- **v0.5** — Seasonal Planning module
- **v0.6** — Custom Events + Season Journal
- **v0.7** — Irrigation module (future)
- **v0.8** — Crop Identification module (extends CropPlanting with image data)
- **v0.9** — Market Data module (extends Crop with pricing, CropPlanting with yield/cost)
