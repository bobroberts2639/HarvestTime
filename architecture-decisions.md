# Harvest Time — Architecture Decisions

## Decision Log

### Decision 1: Modular Monolith
**Status:** ✅ Locked (2026-07-29)
**Context:** Team debate on single app vs. suite of services
**Decision:** One backend application, one data model, domain-specific service boundaries
**Rationale:** Farmers won't open five different apps. The value is in integration — weather connects to fields connects to recommendations. Split the services, not the app.
**Dissent:** None — team consensus

### Decision 2: Tech Stack
**Status:** ✅ Locked (2026-07-29)
**Context:** Need to pick languages, frameworks, databases
**Decision:** Python + FastAPI, React + Next.js PWA, PostgreSQL + PostGIS
**Rationale:** Python has the best ag data science ecosystem. Next.js gives SSR for slow connections. PostGIS handles spatial field data. All free/open source.

### Decision 3: Weather Provider
**Status:** ✅ Locked (2026-07-29)
**Context:** Need reliable weather data with agricultural endpoints
**Decision:** Open-Meteo (primary) with Visual Crossing (fallback)
**Rationale:** Open-Meteo is free, no API key needed, has ag-specific endpoints (ET₀, soil temp). Visual Crossing provides redundancy via circuit breaker.

### Decision 4: Recommendation Engine
**Status:** ✅ Locked (2026-07-29)
**Context:** How to generate advice
**Decision:** Rule-based for MVP, ML deferred to V2+
**Rationale:** Agronomist-defined rules per crop × growth stage × weather condition. Auditable, predictable, no training data needed. ML comes after we have enough user feedback data.

### Decision 5: MVP Geography
**Status:** ✅ Locked (2026-07-29)
**Context:** Where to launch first
**Decision:** US only
**Rationale:** USDA SSURGO soil data, NOAA weather resolution, US-friendly regulatory landscape. Expansion later.

### Decision 6: Offline Strategy
**Status:** ✅ Locked (2026-07-29)
**Context:** Farmers work in fields with intermittent connectivity
**Decision:** Cache-first, sync-when-possible PWA
**Rationale:** Weekly advice cached locally, works 7 days without connectivity (~50KB/field/week — works on 2G). Data freshness always visible.

### Decision 7: Ownership Layer
**Status:** ✅ Locked (2026-07-29)
**Context:** Farmers need to feel ownership for long-term retention
**Decision:** Field notes, recommendation feedback, user preferences in V1. Calendar, journal, ownership dashboard in V2-V3.
**Rationale:** Three farmer-authored interactions per week (respond to rec, add note, review history) forms the ownership habit. Switching costs increase with accumulated data.
