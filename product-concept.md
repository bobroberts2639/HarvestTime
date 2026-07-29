# Harvest Time — Product Concept

## Vision

A smart farming advisor that combines real-time weather intelligence with agronomic science to give farmers actionable recommendations — not just data, but decisions.

## Core Problem

Farmers juggle fragmented tools: weather apps that don't understand crops, soil data that doesn't connect to forecasts, and generic advice that ignores their local conditions. The result is guesswork where precision matters most.

## What We Build

An integrated platform that answers the farmer's question: "What should I do this week, given my crops, my soil, and the weather coming?"

## Key Features

### 1. Field Profile
Farmers register their fields: location, soil type, crops planted, growth stage. The agronomic data model captures what matters (pH, drainage, organic matter, crop variety).

### 2. Weather Intelligence Dashboard
Hyperlocal forecasts, frost alerts, precipitation windows, growing degree day tracking. Not raw weather data — translated into agricultural context ("spray window closing in 36 hours").

### 3. Weekly Action Advisor (Hero Feature)
A weekly briefing combining weather forecast + crop stage + soil conditions → prioritized recommendations. "Apply nitrogen before Thursday's rain" / "Delay planting — soil temp below threshold" / "Harvest in 3-day dry window."

### 4. Alert System
Real-time notifications for critical weather events: frost warnings, heat stress, severe storms. Crop-specific thresholds (a frost alert means different things for wheat vs. citrus).

### 5. Seasonal Planning
Long-range climate outlooks mapped to planting/harvest schedules. Crop rotation recommendations based on soil health data.

### 6. Farmer Ownership & Personalization
- Field notes and season journal
- Calendar overrides and custom events
- User preferences that shape recommendations
- Custom alert thresholds
- Feedback loop (done/skip) that improves future advice
- "My Harvest Time" ownership dashboard

## Design Principles

1. **Decisions, not data** — farmers want to know what to do, not read dashboards
2. **Ownership by accumulation** — the app gets more valuable the more they use it
3. **Capture-first, organize-later** — notes should be effortless, not homework
4. **Personalization as discovery** — preferences surface in-context, not behind Settings
5. **Offline-first** — works in the field with intermittent connectivity

## Tech Stack

- **Backend:** Python + FastAPI
- **Frontend:** React + Next.js (PWA)
- **Database:** PostgreSQL + PostGIS
- **Weather:** Open-Meteo (primary), Visual Crossing (fallback)
- **Hosting:** Railway (MVP) → AWS (scale)

## Architecture

Modular monolith — one backend application, one data model, domain-specific service boundaries. Clean APIs between modules.

## Target

- **MVP:** US only, 5-8 major row crops, rule-based engine
- **Pricing:** Free during beta
- **Platform:** Responsive web (PWA), mobile-first
