# Harvest Time — MVP Scope Definition

## Core Principle

Ship the Weekly Action Advisor. A farmer opens the app, tells it about their fields, and gets useful, field-specific advice for this week. Everything else layers on top.

---

## V1 (MVP, 8 weeks) — Core Advisory + Ownership Foundation

| Feature | MVP Shape | Why It Ships |
|---------|-----------|--------------|
| **Weekly Action Advisor** | One weekly briefing per field: top 3–5 prioritized recommendations derived from forecast + crop stage + soil zone. Rule-based engine. | The killer feature. This is what we're validating. |
| **Field Profile** | Manual entry: location (GPS/zip), crop type, planting date, soil type (USDA SSURGO auto-fill by default). | Minimum context needed for any recommendation. |
| **Weather Intelligence** | One API (Open-Meteo). 7-day forecast, precipitation windows, frost alerts. Translated to agricultural context. | The weather data is the engine. |
| **Push/Browser Notifications** | Frost alerts, severe weather, time-sensitive windows. | High-urgency alerts drive retention. |
| **Basic Auth & Account** | Email/password or social login. One account, multiple fields. | Necessary for data ownership. |
| **Field Notes** | Text + photo, timestamped, tags. Quick-capture from multiple screens. | Ownership anchor #1 — "I wrote this" |
| **Recommendation Feedback** | Done/skipped/modified/dismissed + custom note. One-tap common reasons. | Ownership anchor #2 + structured feedback data |
| **User Preferences** | Units, language, organic mode toggle, seasonal goals, basic alert thresholds. | Ownership anchor #3 — app adapts to them |
| **Recommendation History** | View past recommendations with completion status and feedback. | Establishes longitudinal value |

### V1 Design Goal
Three farmer-authored interactions per week: (1) respond to recommendation, (2) add field note, (3) review history. This forms the ownership habit.

### V1 Constraints
- **Platform:** Responsive web (PWA), works on phone in field
- **Weather API:** Open-Meteo only (swap later if needed)
- **Crop coverage:** 5–8 major row crops (corn, soy, wheat, cotton, rice, potato, tomato, citrus)
- **Geography:** US only
- **Recommendation engine:** Rule-based (not ML)
- **Pricing:** Free during beta

---

## V2 (12 weeks) — Custom Calendar + Journal + Adaptive Recs

| Feature | Why V2 |
|---------|--------|
| Custom calendar events (labor, equipment, contracts) | Farmers need schedule-aware advice |
| Season journal (end-of-season reflections) | Year-over-year value |
| Adaptive recommendations (weighted heuristics from feedback) | Feedback loop closes — app improves per farmer |
| Custom alert rules (advanced thresholds per crop) | Power user personalization |
| Photo gallery view | Richer field notes |
| Historical data import | Bring existing records in |

### V2 Feedback Loop
Per-farmer skip rates adjust rule priority. Still auditable, not ML. >70% skip/dismises demotes a category; >70% done/accepted boosts.

---

## V3 (16 weeks) — Ownership Dashboard + YoY Intelligence

| Feature | Why V3 |
|---------|--------|
| "My Harvest Time" dashboard | Makes investment visible |
| Year-over-year comparisons | Long-term pattern recognition |
| Yield tracking | Connect advice to outcomes |
| Community benchmarks | Anonymized peer comparison |
| Export/share | Data portability |
| Advanced analytics | Deep insights |

### V3 Feedback Loop
Pattern analysis — correlation insights, regional benchmarks. Potential ML transition.

---

## Success Metrics

| Metric | Target | What It Tells Us |
|--------|--------|-----------------|
| **Weekly return rate** | ≥40% of active users open app in any given week | Core loop is sticky |
| **Advisory engagement** | ≥60% of users who open app interact with weekly advisory | Feature delivers value |
| **Alert click-through** | ≥25% of frost/severe alerts result in app open | Alerts drive action |
| **Field profile completion** | ≥50% of signups create ≥1 field in first session | Onboarding isn't a wall |
| **Feedback rate** | ≥50% of recommendations get done/skip response | Ownership habit forming |
| **Net feedback** | Ask 10 beta farmers "Would you pay for this?" | Demand signal |

---

## MVP Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Wrong recommendations erode trust | High | Conservative rules, "report issue" button, agronomist review before launch |
| Weather data gaps in rural areas | Medium | Use gridded forecast models (HRRR via Open-Meteo), not station-only |
| Cold start — users don't fill in field data | High | SSURGO auto-fill, GPS defaults, crop type is only required field |
| Notes feel like homework | Medium | Capture-first design, auto-tags, voice notes, no required fields |
| Seasonal churn | Medium | Natural for ag apps. Acknowledge in metrics. |

---

## If We Need to Cut Further

Priority order:
1. Multiple fields → one field per account
2. Notifications → in-app only, no push
3. Weather translation → show forecast + basic interpretation
4. SSURGO auto-fill → pure manual entry

**Never cut:** The weekly advisory. That's the whole point.
