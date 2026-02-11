# Girchi Digital Policy

Decentralized political governance platform for [Girchi](https://girchi.com) — enabling transparent elections, community self-organization, and citizen engagement through a tiered leadership hierarchy.

## Monorepo Structure

```
policy/
  backend/          Django API server
  mobile/           Expo mobile app (iOS/Android)
  web/              (planned) Web frontend
```

### [`backend/`](backend/)

Django 6 REST API powering the platform.

- **Stack:** Django 6 / DRF / PostgreSQL 16 / Redis 7 / Celery / JWT auth
- **Apps:** accounts, verification, territories, (communities, governance, sos, initiatives, arbitration, gamification — planned)
- **Run:** `docker-compose up -d` → API at `localhost:8000`, docs at `/api/docs/`

### [`mobile/`](mobile/)

Expo mobile app — currently a clickable prototype, evolving into production.

- **Stack:** Expo SDK 54 / TypeScript / Expo Router v4
- **Status:** Prototype with 16 screens, Georgian text, mock data
- **Run:** `cd mobile && npm install && npx expo start` → scan QR with Expo Go

## Documentation

| Document | Description |
|----------|-------------|
| [`init.md`](init.md) | Primary specification (Georgian) — full application logic, roles, governance |
| [`TECH_SPEC.md`](TECH_SPEC.md) | Backend technical specification — models, endpoints, permissions, infrastructure |
| [`MOBILE_SPEC.md`](MOBILE_SPEC.md) | Mobile design specification — 47 screens, design system, navigation, API mapping |
| [`BACKLOG.md`](BACKLOG.md) | Backend implementation backlog — 68 tasks across 6 phases |
| [`MOBILE_BACKLOG.md`](MOBILE_BACKLOG.md) | Mobile implementation backlog — 73 tasks across 7 phases |
| [`CLAUDE.md`](CLAUDE.md) | AI assistant context for Claude Code |

## Domain Concepts

- **GeDer** — verified GeD (Girchi e-Democracy) holder, the system's core participant
- **Endorsed Supporter** — non-GeD member sponsored by a GeDer who acts as guarantor
- **Groups of 10 (ათეული)** — base organizational unit; 10 members elect an Atistavi (leader)
- **Governance Hierarchy** — Atistavi → 50-leader → 100-leader → 1000-leader → Council
- **SOS System** — crisis reporting with moral filter, local verification, escalation chain
- **Gamification** — territory progress tiers unlock capabilities (arbitration, budget, media)

## External Integrations

| Service | Purpose |
|---------|---------|
| [girchi.com](https://girchi.com) (Strapi) | GeD verification, user JWT auth |
| [smsoffice.ge](https://smsoffice.ge) | SMS OTP delivery |

## Implementation Status

| Component | Progress | Current Phase |
|-----------|----------|---------------|
| Backend API | Phase 2 in progress | Territories & onboarding |
| Mobile App | Prototype complete | Evolving to production (Phase 0) |
| Web Frontend | Not started | — |
