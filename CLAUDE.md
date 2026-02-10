# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

This file has an overview of the project but always consult original init.md before making any decisions.

## Repository Overview

This is a **policy and specification repository** (not a codebase) for the Girchi Digital Policy application — a decentralized political governance platform. All documents are written in **Georgian (ქართული)**.

## Documents

- **`init.md`** — Primary specification (Georgian) defining the full application logic: user roles, registration/verification flow, governance hierarchy, gamification, and security mechanisms
- **`TECH_SPEC.md`** — Comprehensive technical specification for the Django backend API: data models, API endpoints, permissions, infrastructure, external integrations
- **`BACKLOG.md`** — Implementation backlog with 65+ tasks across 6 phases, priorities, acceptance criteria, and dependency graph
- **`Girchi.com.postman_collection.json`** — Postman collection for existing girchi.com API (GeD data source)
- **`SMS.md`** — Reference link to SMS integration API (smsoffice.ge)
- **`GED.md`** — Placeholder for GeD (digital ID) documentation

## Backend Stack

Django 5.1+ / DRF / PostgreSQL 16 / Redis 7 / Celery / JWT auth / Docker

9 Django apps: `accounts`, `verification`, `territories`, `communities`, `governance`, `sos`, `initiatives`, `arbitration`, `gamification`

External integrations: girchi.com Strapi API (GeD verification, user JWT auth), smsoffice.ge (SMS OTP)

## Key Domain Concepts

- **User Roles:** Unverified users → GeDers (verified ID holders, system core) → Endorsed Supporters (non-GeD holders sponsored by a GeDer who acts as guarantor)
- **Statuses:** Passive members (vote only) vs. Active members (public positions, eligible for leadership)
- **Governance Hierarchy:** Atistavi (10s leader) → 50-leader → 100-leader → 1000-leader → Council. Each tier is elected from within the tier below.
- **Endorsement System:** GeDers vouch for supporters with a limited endorsement quota. If an endorsed user turns out to be fake/harmful, the endorser faces penalties — this drives self-regulation.
- **SOS System:** Crisis reporting with moral filtering, local verification by Atistavi, then escalation through the hierarchy up to media.
- **Gamification Loop:** More members → new tier → more powers/budget → motivation to recruit → growth cycle.
- **Territorial Assignment:** Users are placed into groups by electoral precinct/district.

