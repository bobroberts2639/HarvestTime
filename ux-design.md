# Harvest Time — UX Design

## Design Principles

1. **Decisions, not data** — farmers want to know what to do, not read dashboards
2. **Mobile-first, field-tested** — works outdoors with sun glare, gloves, slow connections
3. **Offline-first** — last plan always available, data freshness always visible
4. **Ownership by accumulation** — the app gets more valuable the more they use it
5. **Capture-first, organize-later** — notes should be effortless, not homework
6. **Personalization as discovery** — preferences surface in-context, not behind Settings

---

## Onboarding (5 screens, <3 min)

1. **Phone OTP** — sign up with phone number
2. **GPS Location** — auto-detect location for weather/soil data
3. **Crop/Field Setup** — select crop type, planting date (USDA SSURGO auto-fills soil data)
4. **Satellite Boundary** (optional) — sketch field boundary via satellite view
5. **Alert Preferences** — choose notification preferences

Skip-able steps. Progressive setup. Crop type is the only required field.

---

## Bottom Navigation (5 tabs)

| Tab | Icon | Purpose |
|-----|------|---------|
| Home | 🏠 | Dashboard with weather, top actions, field status |
| Advisor | 📋 | Weekly Action Advisor — the hero feature |
| Fields | 🌾 | Field management and details |
| Settings | ⚙️ | Preferences, alerts, account |
| My Harvest | 🌟 | Ownership dashboard — seasons, stats, knowledge |

---

## Core Screens (15 total)

### 1. Onboarding (see above)

### 2. Home Dashboard
Single-column mobile layout:
- Persistent weather bar (current conditions + 3-day summary)
- Weekly Advisor preview (3 priority-coded action cards)
- 10-day forecast scroll
- Field status cards (growth stage, soil moisture, next action)
- Quick Actions row (add note, view alerts, update field)

### 3. Weekly Advisor (Hero Feature)
Sunday evening personalized action plan fusing weather + crop stage + soil + pest models + regulatory windows.

**Three priority tiers:**
- 🔴 **Urgent (48hr)** — time-critical actions
- 🟡 **This Week** — important but flexible
- 🟢 **FYI** — informational, no action needed

Each card has:
- **"Why" toggle** — shows plain-language reasoning
- **Done/Skip buttons** — with one-tap common reasons
- **Notes** — optional context for feedback

### 4. Action Detail
Full recommendation view with:
- Detailed reasoning (weather context, crop stage, soil conditions)
- Step-by-step action items
- Estimated effort and deadline
- Related recommendations
- Skip/modify options

### 5. Fields List
List view with status dots (green=growing, yellow=needs attention, gray=harvested)

### 6. Field Detail
Three-tab view:
- **Map** — satellite boundary, weather overlay
- **Data** — crop info, soil profile, growth stage (GDD-based), upcoming actions
- **Notes** — field notes timeline with search + tag filter

### 7. Field Notes
Quick-note capture from Field Detail, Home, or Advisor cards:
- Text input with auto-tags from context
- Photo-first mode (camera → note)
- Voice notes
- Timeline view with search + tag filtering
- Offline sync — notes queue when offline

### 8. Alert Inbox
All active and past alerts, filterable by type and severity.

### 9. Weather Detail
Expanded weather view with hourly forecasts, precipitation probability, wind, soil temperature.

### 10. Settings
- **Notification Preferences** — per-alert-type toggles
- **Custom Thresholds** — frost, heat, soil moisture, wind (editable per farmer)
- **Organic Mode** — swaps synthetic recs for OMRI-listed alternatives
- **Units** — metric/imperial
- **Language** — multilingual support
- **Seasonal Goals** — 1-3 goals that shape recommendations
- **Preferred Products** — products list for recommendations
- **Equipment List** — equipment for scheduling

**Key design:** Preferences surface in-context (tap ⚙️ on any alert) not just behind Settings.

### 11. Season Journal (V2)
End-of-season summary:
- Stats: recommendations completed, notes captured, weather summary
- Reflection prompts: what went well / what differently / biggest surprise / app help
- Year-over-year comparison view with visual trends
- Auto-generated "what I learned" insights

### 12. My Calendar (V2)
Personal events alongside advisor recommendations:
- Unified timeline: advisor recs (colored) + personal events (purple)
- Drag-to-reschedule advisor recs with smart conflict warnings
- "My Schedule" filter to hide advisor recs
- Event creation with type chips (labor, equipment, contract, market) + field linking

### 13. Recommendation History
View past recommendations with:
- Completion status and feedback
- Skip reasons summary
- "Your feedback improved 12 recommendations this season" impact message

### 14. My Harvest (Ownership Dashboard) (V3)
🌟 tab showing:
- Seasons completed, fields managed
- Recommendations followed, notes/photos captured
- Knowledge summary (top field, top tag, trends)
- Value proof moments after completing recs, capturing notes

### 15. Season Review (V3)
Year-over-year comparison with visual trends and auto-generated insights.

---

## Mobile-First Considerations

- **WCAG AAA contrast** for sun glare readability
- **48px+ touch targets** for gloved hands
- **Service worker offline caching** — last plan always available
- **PWA installable** — add to homescreen, native-app feel
- **One-handed bottom-nav layout** — thumb-reachable
- **3-second scan design** — critical info visible in 3 seconds

---

## Interaction Patterns

### Done/Skip Flow
1. Tap "Done" → confirmation animation → feedback recorded
2. Tap "Skip" → one-tap reason chips ("already handled", "not applicable", "too expensive", "I disagree") + free text option
3. No judgment UI — skip is a valid response

### Note Capture
1. Tap "+" from any screen → note capture overlay
2. Type or speak → auto-tags from context (field, crop, weather, date)
3. Add photo (optional) → saved offline, synced when connected
4. Done → brief confirmation, return to previous screen

### Preference Discovery
1. See alert → tap ⚙️ on alert → "Change threshold for this alert type"
2. See recommendation → tap "Why" → "This recommendation is because..."
3. Settings → "Personalize recommendations" → guided flow

---

## Risk Mitigations

| Risk | Mitigation |
|------|------------|
| Notes feel like homework | Capture-first design, no required fields, auto-tags, voice notes |
| Calendar busyness | Start with advisor-only view, personal events opt-in |
| Preference complexity | In-context discovery, sensible defaults, guided setup |
| Ownership dashboard vanity metrics | Focus on actionable stats, not just counts |
