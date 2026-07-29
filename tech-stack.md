# Harvest Time — Tech Stack

## 1. Backend: Python + FastAPI

**Why Python:** Best ecosystem for agricultural data science — NumPy, pandas, scikit-learn for recommendation engine. Massive talent pool. Every weather/soil/crop API has a Python SDK or trivial client.

**Why FastAPI:** Async-native (handles concurrent weather API calls well), auto-generated OpenAPI docs, Pydantic validation baked in, high performance comparable to Node/Go for I/O-bound work.

**Modular monolith structure:** Each domain (weather, crops, fields, alerts, recommendations) lives as a Python module with its own models, services, and API routes — all in one deployable. Use FastAPI's native DI to keep boundaries clean without microservice overhead.

---

## 2. Frontend: React + Next.js (PWA)

**Why Next.js:** SSR for fast initial load on slow mobile connections. Static generation for marketing/info pages.

**Why PWA:** Critical for farmers in the field — service workers cache key screens (field profiles, latest recommendations, weather summary) for offline access. Add to Home Screen gives native-app feel without app store friction.

**Key libs:** TanStack Query (caching + offline sync), Recharts (weather charts), Leaflet (field mapping), Tailwind CSS (mobile-first responsive), Workbox (PWA service worker).

---

## 3. Database: PostgreSQL + PostGIS

Single relational database — fits monolith philosophy.

- **PostgreSQL 16+** — rock-solid, free, handles structured crop/weather data
- **PostGIS extension** — field boundaries are polygons, weather is spatial. Queries like 'fields near this weather station' are native.
- **pg_cron** — scheduled jobs for weather fetches, recommendation generation

---

## 4. Weather API Integrations

- **Open-Meteo** (primary) — 7-day forecasts, hourly data, ag-specific endpoints (soil temp, evapotranspiration). Free for non-commercial, ~20/mo commercial.
- **NOAA CAP** (severe alerts) — government storm/frost/flood warnings. Free.
- **Tomorrow.io or OpenWeatherMap** (backup) — fallback for global coverage.

---

## 5. Hosting: Railway (MVP) → AWS (Scale)

**MVP:** Railway or Fly.io — PostgreSQL + PostGIS native, git-push deploy, $5-20/mo.
**Scale:** AWS ECS Fargate + RDS PostgreSQL + CloudFront.

---

## 6. Key Libraries & Tools

**Backend:** FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2, httpx, Celery+Redis, Jinja2
**Frontend:** Next.js 14+, React 18+, TanStack Query, Tailwind, Leaflet, Recharts, Workbox, Zustand
**DevOps:** Docker, GitHub Actions, Ruff (Python linting), Biome (JS/TS linting), pytest

---

## 7. Key Principles

- Offline-first PWA for field reliability
- Mobile-first responsive (320px-1440px, large touch targets)
- Cost-effective MVP (Open-Meteo free, Railway $5-20/mo)
- Clean scale path (monolith → containerized → ECS)
- PostGIS for spatial agricultural data
- Two type-safe languages (Python + TypeScript)
