# Frontend — Next.js App

This is the Harvest Time frontend — a responsive PWA built with Next.js, React, and Tailwind CSS.

## Getting Started

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Tech Stack

- **Framework:** Next.js 14+ (App Router)
- **UI:** React 18+, Tailwind CSS
- **State:** TanStack Query (server state), Zustand (client state)
- **Maps:** Leaflet (field mapping)
- **Charts:** Recharts (weather visualization)
- **PWA:** Workbox (offline caching)
- **API:** REST endpoints at `/api/v1/`

## Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── layout.tsx          # Root layout with providers
│   ├── page.tsx            # Home dashboard
│   ├── advisor/            # Weekly Advisor page
│   ├── fields/             # Field management
│   │   ├── page.tsx        # Fields list
│   │   └── [id]/           # Field detail
│   ├── notes/              # Field notes
│   ├── settings/           # Preferences & customization
│   ├── my-harvest/         # Ownership dashboard
│   └── api/                # API routes (BFF)
├── components/             # Reusable UI components
│   ├── ui/                 # Base components (Button, Card, etc.)
│   ├── weather/            # Weather-specific components
│   ├── recommendations/    # Recommendation cards
│   └── fields/             # Field management components
├── lib/                    # Utilities and API clients
│   ├── api.ts              # API client
│   └── hooks/              # Custom React hooks
└── public/                 # Static assets, PWA manifest
```

## PWA Configuration

- Service worker caches key screens for offline access
- Installable via "Add to Home Screen"
- Works on phone in the field with intermittent connectivity
- Last plan always available offline

## Mobile-First Design

- 320px-1440px responsive
- 48px+ touch targets (gloves-friendly)
- WCAG AAA contrast (sun glare readable)
- One-handed bottom navigation
- 3-second scan design
