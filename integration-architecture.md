# Harvest Time — Integration Architecture

## External API Integrations

### Weather Data (Critical Path)
- **Primary: Open-Meteo** — Free tier, no API key, global coverage, hourly/daily forecasts, agricultural endpoints (ET₀, soil temperature). Latency: ~200ms. Reliability: 99.9%.
- **Fallback: Visual Crossing Weather API** — Free tier 1000 calls/day, good agricultural data. Activated via circuit breaker when Open-Meteo fails.
- **Premium upgrade path: Tomorrow.io** — Hyperlocal, minute-by-minute. When we need field-level precision.
- **Refresh cadence:** Every 6 hours for 7-day forecast; every 30 min for severe weather alerts.

### Soil Data (Secondary)
- **OpenLandMap / SoilGrids (ISRIC)** — Free global soil data (texture, pH, organic carbon, moisture) at 250m resolution.
- **USDA SSURGO API** — US-only but extremely detailed (field-level).
- **Refresh cadence:** Soil data is slow-changing. Pull on field creation + monthly refresh.

### Market Data (Tertiary)
- **USDA AMS (Agricultural Marketing Service)** — Free daily market prices for major crops.
- **Trading Economics API** — Commodity futures, broader coverage. Paid tier needed.
- **Refresh cadence:** Daily at market close.

### Geocoding
- **Nominatim (OpenStreetMap)** — Free, no key. Convert field addresses → coordinates.

---

## Internal Module Interfaces

Modular monolith with domain-specific service boundaries. Cross-module communication is synchronous function calls (single process = low latency).

### Module Map

| Module | Exposes | Consumes |
|--------|---------|----------|
| **WeatherModule** | `getForecast(fieldId, days)`, `getAlerts(fieldId)`, `getCurrentConditions(fieldId)` | FieldProfileModule |
| **CropModule** | `getCropStage(fieldId)`, `getGDD(fieldId)`, `getCropCalendar(cropType)` | WeatherModule |
| **FieldProfileModule** | `getField(fieldId)`, `listFields(userId)`, `getFieldCoordinates(fieldId)` | — (leaf) |
| **RecommendationEngine** | `generateWeeklyAdvice(fieldId)`, `getPrioritizedActions(fieldId)` | WeatherModule, CropModule, SoilModule, MarketModule |
| **AlertModule** | `createAlert(...)`, `checkThresholds(...)`, `getActiveAlerts(userId)` | WeatherModule, RecommendationEngine |
| **NotificationModule** | `send(notification)`, `scheduleReminder(...)`, `getPreferences(userId)` | AlertModule, RecommendationEngine |
| **IrrigationModule** | `getSchedule(fieldId)`, `calculateET(fieldId)`, `adjustForRain(forecast)` | WeatherModule, CropModule, FieldProfileModule |
| **SoilModule** | `getSoilProfile(fieldId)`, `getLastAnalysis(fieldId)` | FieldProfileModule |
| **MarketModule** | `getPrice(cropType)`, `getTrend(cropType, days)` | CropModule |

### Key Design Rule
The Recommendation Engine is the only module that reads from all others. Other modules never call each other directly — they go through the engine. Clean dependency graph.

---

## Third-Party Dependencies & Fallback

| Service | Criticality | Fallback | Degradation |
|---------|-------------|----------|-------------|
| Weather API | **Critical** | Circuit breaker → secondary API → cached forecast | Show stale forecast with "last updated" timestamp |
| Soil Data | Medium | Cache aggressively, use regional defaults | Show regional averages, mark as approximate |
| Market Data | Low | Cache daily prices | Show "prices as of [date]" |
| Geocoding | Medium | Cache coordinates, manual lat/lng input | Let user enter coordinates directly |
| SMS Provider | High | Fallback to push + email | Log alert, retry SMS on next connectivity |

### Circuit Breaker Pattern
- 5 failures in 5 minutes → open circuit for 30 minutes
- Half-open: allow 1 request through every 5 minutes to test recovery
- All external calls wrapped in timeout (5s default, 15s for weather batch)

---

## Offline / Low-Connectivity

### Strategy: Cache-First, Sync-When-Possible
- **Last-known state always available** — weather, crop calendar, soil data, previous recommendations cached locally (IndexedDB)
- **Weekly advice generated and cached** — works offline for 7 days, degrades gracefully if forecast is stale
- **Field data synced on create/edit** — last-write-wins conflict resolution
- **Alert queueing** — critical alerts (frost, hail) attempt immediate delivery via SMS even on 2G
- **Service worker for web** — PWA architecture, serve from cache when offline
- **Data freshness indicator** — always show "Weather data: 4 hours old"

### Bandwidth Budget
- Weather data: ~2KB/day of forecast
- Weekly advice text: ~5KB
- Field profiles: ~1KB each
- Total weekly sync per field: ~50KB — works on 2G

---

## Notification Infrastructure

### Three Channels, Escalating Urgency

| Channel | Use Case | Latency | Cost |
|---------|----------|--------|------|
| **Push (FCM/APNs)** | Weekly advice, routine updates | Minutes | Free |
| **SMS (Twilio)** | Severe weather, frost warnings | < 2 min | ~$0.01/msg |
| **Email** | Weekly digest, seasonal reports | Hours OK | Free |

### Priority Levels
- **P0 (Emergency):** Frost, hail, severe storm → SMS + Push simultaneously
- **P1 (High):** Irrigation needed today, pest alert → Push notification
- **P2 (Medium):** Weekly advice ready, market movement > 10% → Push notification
- **P3 (Low):** Seasonal tips, market digest → Email

### Scheduling
- Weekly advice: generated Sunday evening, delivered Monday 6am
- Weather alerts: evaluated every 30 minutes
- Market digest: daily 7am via email

---

## Key Decisions
1. Open-Meteo as primary weather — free, reliable, agricultural endpoints
2. Recommendation Engine as single orchestrator — no module-to-module cross-calls
3. Cache-first for offline — weekly advice cached locally, works 7 days without connectivity
4. SMS reserved for emergencies only — cost control + urgency signal
5. Circuit breakers on all external calls — never let a down API bring down the product
6. Data freshness is always visible — farmers need to trust what they're reading
