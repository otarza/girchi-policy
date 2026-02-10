# Girchi Digital Policy — Implementation Backlog

> Priority: P0 = must have, P1 = should have, P2 = nice to have
> Status: `[ ]` = todo, `[x]` = done, `[-]` = skipped

> **Last updated:** 2026-02-10
> **Current phase:** Phase 1 complete (except tests/CI). Ready for Phase 2.

---

## Phase 1: Foundation (Weeks 1–2) — COMPLETE

**Goal:** Project scaffolding, user registration, phone verification, JWT auth.

### Sprint 1.1 — Project Setup

- [x] **GP-001** [P0] Initialize Django 6.0 project with split settings
  - `config/` package with `settings/base.py`, `settings/dev.py`, `settings/prod.py`
  - `django-environ` for environment variable management
  - `.env.example` with all required variables
  - **Done:** `python manage.py check` passes. Django 6.0.2 with Python 3.12+ practices.

- [x] **GP-002** [P0] Docker and Docker Compose setup
  - `Dockerfile` (Python 3.12-slim)
  - `docker-compose.yml` with 5 services: web, db (PostgreSQL 16), redis, celery_worker, celery_beat
  - `django-celery-beat` installed via `--no-deps` due to Django 6 version cap
  - **Done:** `docker-compose up -d` starts all services, Django responds at localhost:8000

- [x] **GP-003** [P0] Create `common/` utilities package
  - `common/mixins.py` — `TimestampMixin`, `SoftDeleteMixin`
  - `common/validators.py` — `validate_georgian_personal_id` (11 digits), `validate_georgian_phone` (+995 format)
  - `common/pagination.py` — `StandardPagination` (page_size=20)
  - `common/permissions.py` — `IsPhoneVerified`, `IsOnboarded`, `IsGeDer`, `IsVerifiedMember`, `IsActiveMember`, `IsNotDiaspora`
  - `common/throttling.py` — `OTPRateThrottle` (5/hour)
  - **Done:** All utilities in place and used by apps.

- [x] **GP-004** [P0] Custom User model (`apps/accounts`)
  - `User` model extending `AbstractUser`, `USERNAME_FIELD = 'phone_number'`
  - Fields: phone_number, personal_id_number, role, member_status, join_reason, constitution_accepted, constitution_accepted_at, onboarding_completed, is_diaspora, is_phone_verified, timestamps
  - `UserManager` with `create_user()` and `create_superuser()`
  - Django admin registration
  - **Done:** Migrations run. Users can be created via API and admin.

- [x] **GP-005** [P0] JWT authentication setup
  - `djangorestframework-simplejwt` 5.5 configured
  - `POST /api/v1/auth/token/` — obtain token pair
  - `POST /api/v1/auth/token/refresh/` — refresh access token
  - Token lifetimes: access=15min, refresh=7days (configurable via env)
  - **Done:** JWT auth working end-to-end.

- [x] **GP-006** [P0] User registration endpoint
  - `POST /api/v1/auth/register/`
  - Validates phone format, personal ID uniqueness, password strength
  - Returns user object (role=unverified)
  - **Done:** Registration tested via curl, returns 201.

- [x] **GP-007** [P0] User profile endpoints
  - `GET /api/v1/auth/me/` — returns full profile
  - `PATCH /api/v1/auth/me/` — update allowed fields
  - `POST /api/v1/auth/me/onboarding/` — onboarding submission
  - **Done:** Profile read/update working.

### Sprint 1.2 — Verification & Async Infrastructure

- [x] **GP-008** [P0] SMS OTP model and service (`apps/verification`)
  - `SMSOTPRequest` model with phone_number, code, attempts, expires_at, is_verified
  - `SMSService` class wrapping smsoffice.ge API
  - OTP generation (6 digits), 5-minute expiry, max 5 attempts
  - **Done:** Service layer complete.

- [x] **GP-009** [P0] SMS OTP endpoints
  - `POST /api/v1/verification/sms/send-otp/` — generate and send OTP
  - `POST /api/v1/verification/sms/verify-otp/` — validate OTP code
  - Rate limiting: 5 requests/hour/phone via `OTPRateThrottle`
  - **Done:** Endpoints wired and throttled.

- [x] **GP-010** [P0] Celery + Redis setup
  - `config/celery.py` — Celery app configuration
  - Redis as broker (DB 1) and cache backend (DB 0)
  - `send_otp_sms` and `cleanup_expired_otps` async tasks
  - celery_worker + celery_beat services in docker-compose
  - **Done:** Celery worker and beat running in Docker.

- [x] **GP-011** [P0] Device fingerprint model and endpoint
  - `DeviceFingerprint` model with fingerprint_hash, device_data (JSON), ip_address, is_flagged
  - `POST /api/v1/verification/device/fingerprint/`
  - Cross-user duplicate detection (flags if same fingerprint for different users)
  - **Done:** Model and endpoint complete.

- [x] **GP-012** [P1] OpenAPI docs setup
  - `drf-spectacular` configured
  - Swagger UI at `/api/docs/`
  - ReDoc at `/api/redoc/`
  - Schema at `/api/schema/`
  - **Done:** Swagger UI renders all endpoints.

- [-] **GP-013** [P1] CI pipeline setup — SKIPPED (deferred)
  - GitHub Actions workflow: lint (ruff), test (pytest), security (bandit)
  - Will set up when repo is pushed to GitHub

- [-] **GP-014** [P0] Write tests for Phase 1 — SKIPPED (deferred)
  - Tests deferred to a dedicated testing pass

### Phase 1 Notes
- **Django 6.0.2** used (released Dec 2025). Key changes from Django 5: `BigAutoField` default, no positional `save()` args, `STORAGES` dict, built-in CSP middleware.
- **`django-celery-beat` workaround:** Package caps `Django<6.0` but works fine. Installed with `--no-deps` via `requirements/nodeps.txt`. Tracked at: https://github.com/celery/django-celery-beat/issues/977
- **GeD verification** models and service also built in Phase 1 (originally Phase 2 scope: GP-015, GP-016). `GeDVerification` model, `GeDService` class, and endpoints (`/ged/verify/`, `/ged/status/`) are complete.

---

## Phase 2: Verification & Onboarding (Weeks 3–4)

**Goal:** Complete onboarding flow, territory system, precinct assignment.

### Sprint 2.1 — GeD & Onboarding

- [x] **GP-015** [P0] GeD verification model and service
  - Completed in Phase 1. `GeDVerification` model and `GeDService` class in `apps/verification/`.

- [x] **GP-016** [P0] GeD verification endpoints
  - Completed in Phase 1. `POST /api/v1/verification/ged/verify/` and `GET /api/v1/verification/ged/status/`.

- [x] **GP-017** [P0] Onboarding endpoint
  - Completed in Phase 1. `POST /api/v1/auth/me/onboarding/` with `IsPhoneVerified` permission.

- [x] **GP-018** [P0] Permission classes (first batch)
  - Completed in Phase 1. All in `common/permissions.py`:
    `IsPhoneVerified`, `IsOnboarded`, `IsGeDer`, `IsVerifiedMember`, `IsActiveMember`, `IsNotDiaspora`

### Sprint 2.2 — Territories

- [ ] **GP-019** [P0] Territory models
  - `Region` (name, name_ka, code)
  - `District` (FK Region, name, name_ka, cec_code)
  - `Precinct` (FK District, name, name_ka, cec_code, lat, lng)
  - Indexes on cec_code fields
  - **AC:** Models created, migrations run, admin registered

- [ ] **GP-020** [P0] `import_cec_data` management command
  - `python manage.py import_cec_data <file_path>`
  - Accepts CSV/JSON with CEC electoral data
  - Creates/updates Region → District → Precinct hierarchy
  - Idempotent (re-run without duplicates)
  - **AC:** Running command populates territory tables. Re-running doesn't create duplicates.

- [ ] **GP-021** [P0] Territory API endpoints
  - `GET /api/v1/territories/regions/`
  - `GET /api/v1/territories/regions/{id}/districts/`
  - `GET /api/v1/territories/districts/{id}/precincts/`
  - `GET /api/v1/territories/precincts/{id}/`
  - `GET /api/v1/territories/precincts/nearby/?lat=&lng=` (simple distance calculation)
  - All read-only, requires auth
  - **AC:** All endpoints return correct data. Nearby search returns precincts within radius.

- [ ] **GP-022** [P0] User precinct assignment
  - `PATCH /api/v1/auth/me/` allows setting `precinct_id`
  - Or auto-assign based on coordinates during onboarding
  - **AC:** User can be assigned to a precinct

- [ ] **GP-023** [P1] Diaspora handling
  - `is_diaspora` flag on User model (already exists)
  - Diaspora users can register and verify but are excluded from local hierarchy
  - `IsNotDiaspora` permission class (already exists)
  - **AC:** Diaspora users cannot join groups or vote in local elections

- [-] **GP-024** [P0] Write tests for Phase 2 — DEFERRED

---

## Phase 3: Communities & Endorsement (Weeks 5–7)

**Goal:** Groups-of-10, endorsement system, community membership.

### Sprint 3.1 — Groups

- [ ] **GP-025** [P0] GroupOfTen and Membership models
  - `GroupOfTen` (FK Precinct, name, is_full, created_at)
  - `Membership` (OneToOne User, FK GroupOfTen, is_active, joined_at, left_at)
  - **AC:** Models created, migrations run

- [ ] **GP-026** [P0] Group endpoints
  - `GET /api/v1/communities/groups/?precinct_id=` — list groups, annotated with member_count
  - `POST /api/v1/communities/groups/` — create group (GeDer only, in own precinct)
  - `GET /api/v1/communities/groups/{id}/` — detail with member list
  - `POST /api/v1/communities/groups/{id}/join/` — join group
  - `POST /api/v1/communities/groups/{id}/leave/` — leave group
  - **AC:** GeDers can create/join groups. Members listed correctly. Non-GeDers cannot create.

- [ ] **GP-027** [P1] Group capacity management
  - Mark group as `is_full` when member_count reaches 10
  - Prevent joining full groups
  - Auto-create LeaderPosition (tier=10) when group is created
  - **AC:** Full groups reject new join requests. Position created on group creation.

### Sprint 3.2 — Endorsement

- [ ] **GP-028** [P0] Endorsement and EndorsementQuota models
  - `Endorsement` (FK guarantor, OneToOne supporter, status, timestamps)
  - `EndorsementQuota` (OneToOne geder, max_slots=10, used_slots, is_suspended)
  - Auto-create quota on GeD verification (via signal or in service)
  - **AC:** Models created. Quota auto-created when user becomes GeDer.

- [ ] **GP-029** [P0] Endorsement endpoints
  - `POST /api/v1/communities/endorsements/` — endorse (guarantor_id implicit from auth)
  - `GET /api/v1/communities/endorsements/` — list given/received
  - `DELETE /api/v1/communities/endorsements/{id}/` — revoke
  - `GET /api/v1/communities/endorsements/quota/` — check quota
  - **AC:** GeDer can endorse within quota. Endorsement creates, lists, revokes correctly.

- [ ] **GP-030** [P0] Endorsement business logic
  - On endorse: check quota, check not suspended, promote supporter role to 'supporter'
  - On revoke: revert supporter role to 'unverified', remove from group, decrement used_slots
  - **AC:** Role promotion and demotion work. Quota enforced. Suspended GeDers cannot endorse.

- [ ] **GP-031** [P1] Nearby GeDers endpoint
  - `GET /api/v1/communities/nearby-geders/?precinct_id=`
  - Returns GeDers in the precinct who have available endorsement slots
  - Used by supporters seeking guarantors
  - **AC:** Returns only GeDers with remaining_slots > 0 and is_suspended = False

- [-] **GP-032** [P0] Write tests for Phase 3 — DEFERRED

---

## Phase 4: Governance & Elections (Weeks 8–11)

**Goal:** Leadership positions, full election lifecycle, hierarchy.

### Sprint 4.1 — Positions & Basic Elections

- [ ] **GP-033** [P0] LeaderPosition model
  - Fields: tier, group FK (tier=10), precinct/district FK (higher tiers), holder FK, held_since, parent FK, is_active
  - Auto-create tier=10 position when GroupOfTen is created (if not done in GP-027)
  - **AC:** Positions created, hierarchy parent-child links work

- [ ] **GP-034** [P0] Election, Candidacy, Vote models
  - `Election` (type, status, position FK, date fields)
  - `Candidacy` (election FK, candidate FK, statement, unique together)
  - `Vote` (election FK, voter FK, candidacy FK, unique together on election+voter)
  - **AC:** Models created, constraints enforced (one vote per election)

- [ ] **GP-035** [P0] Atistavi election endpoints
  - `POST /api/v1/governance/elections/` — create election for a position
  - `POST /api/v1/governance/elections/{id}/nominate/` — register candidacy (IsActiveMember)
  - `POST /api/v1/governance/elections/{id}/vote/` — cast vote (IsVerifiedMember, group member)
  - `GET /api/v1/governance/elections/{id}/results/` — vote tallies
  - **AC:** Full atistavi election lifecycle works: create → nominate → vote → results

- [ ] **GP-036** [P0] Election lifecycle management
  - Status transitions: nomination → voting → completed
  - Validate: can only nominate during nomination phase, vote during voting phase
  - `tally_election_results` Celery task: count votes, determine winner, assign to position
  - `close_expired_elections` periodic task: auto-transition past voting_end
  - **AC:** Status transitions enforced. Winner assigned to position after tally.

### Sprint 4.2 — Hierarchy Elections

- [ ] **GP-037** [P0] Hierarchy election logic
  - 50-leader election: voters = 5 atistavis, candidates from among them
  - 100-leader election: voters = 2 fifty-leaders, candidates from among them
  - 1000-leader election: voters = 10 hundred-leaders, candidates from among them
  - Validate voter eligibility based on tier
  - **AC:** Each hierarchy tier election restricts voters to correct set of leaders

- [ ] **GP-038** [P0] Council member auto-assignment
  - When a user becomes 1000-leader, automatically flag as council (satatbiro) member
  - (This could be a computed property or a flag on LeaderPosition)
  - **AC:** 1000-leaders identified as council members in API responses

- [ ] **GP-039** [P1] Parliamentary list election
  - Separate election_type='parliamentary'
  - All GeDers can vote (no territorial restriction)
  - No position FK (party-level election)
  - **AC:** Parliamentary election works with GeDer-only voter pool

- [ ] **GP-040** [P0] Position and election list endpoints
  - `GET /api/v1/governance/positions/?tier=&precinct_id=&district_id=`
  - `GET /api/v1/governance/elections/?status=&election_type=`
  - **AC:** Filterable list endpoints return correct data

- [ ] **GP-041** [P1] Hierarchy tree endpoint
  - `GET /api/v1/governance/hierarchy/?district_id=`
  - Returns nested tree: 1000-leader → 100-leaders → 50-leaders → atistavis
  - **AC:** Tree correctly represents hierarchy for visualization

- [ ] **GP-042** [P0] Governance permission classes
  - `IsActiveMember` — for candidacy (already exists in common/permissions.py)
  - `IsAtistavi` — for SOS verification
  - `IsLeaderAtTier(min_tier)` — parameterized, for election creation and arbitration
  - `IsNotDiaspora` — exclude diaspora from local elections (already exists)
  - **AC:** All permissions work correctly in endpoint tests

- [-] **GP-043** [P0] Write tests for Phase 4 — DEFERRED

---

## Phase 5: Community Powers (Weeks 12–15)

**Goal:** SOS, initiatives/petitions, arbitration.

### Sprint 5.1 — SOS System

- [ ] **GP-044** [P0] SOS models
  - `SOSReport` (reporter, status, escalation_level, title, description, moral_filter_answer, assigned_to)
  - `SOSEscalation` (report FK, from_level, to_level, escalated_by, note)
  - **AC:** Models created, migrations run

- [ ] **GP-045** [P0] SOS creation and assignment
  - `POST /api/v1/sos/reports/` — create report with moral filter answer
  - `assign_sos_to_atistavi` Celery task: find reporter's group → find atistavi → assign
  - `GET /api/v1/sos/reports/` — list own reports + assigned reports
  - **AC:** Report created, auto-assigned to local atistavi

- [ ] **GP-046** [P0] SOS lifecycle endpoints
  - `POST /api/v1/sos/reports/{id}/verify/` — atistavi confirms (IsAtistavi + is assigned)
  - `POST /api/v1/sos/reports/{id}/reject/` — reject as false
  - `POST /api/v1/sos/reports/{id}/escalate/` — escalate to next tier
  - `POST /api/v1/sos/reports/{id}/resolve/` — mark resolved
  - **AC:** Full SOS lifecycle works with proper permission checks

- [ ] **GP-047** [P0] SOS escalation chain
  - Escalation levels: 10 → 50 → 100 → 1000 → 9999 (media)
  - On escalate: create SOSEscalation record, reassign to appropriate leader at new tier
  - `escalate_sos_timeout` periodic task: auto-escalate if pending > 24 hours
  - **AC:** Escalation creates audit trail, reassigns correctly, auto-escalation works

### Sprint 5.2 — Initiatives

- [ ] **GP-048** [P0] Initiative models
  - `Initiative` (author, title, description, status, precinct/district FK, signature_threshold, response fields)
  - `InitiativeSignature` (initiative FK, signer FK, unique together)
  - **AC:** Models created

- [ ] **GP-049** [P0] Initiative endpoints
  - `GET /api/v1/initiatives/` — list, filterable by status, precinct, district
  - `POST /api/v1/initiatives/` — create initiative
  - `GET /api/v1/initiatives/{id}/` — detail with signature count
  - `POST /api/v1/initiatives/{id}/sign/` — sign (one per user)
  - `DELETE /api/v1/initiatives/{id}/sign/` — withdraw signature
  - **AC:** Full initiative lifecycle works

- [ ] **GP-050** [P0] Initiative threshold and response
  - `check_initiative_thresholds` periodic task: when signatures >= threshold, update status to 'threshold_met'
  - `POST /api/v1/initiatives/{id}/respond/` — representative response (IsLeaderAtTier for territory)
  - **AC:** Threshold detection works. Representative can respond.

### Sprint 5.3 — Arbitration

- [ ] **GP-051** [P0] ArbitrationCase model
  - Fields: case_type, status, complainant/respondent/arbitrator FK, tier, title, description, evidence, decision_text, related_endorsement FK
  - **AC:** Model created

- [ ] **GP-052** [P0] Arbitration endpoints
  - `GET /api/v1/arbitration/cases/` — list (own cases + assigned as arbitrator)
  - `POST /api/v1/arbitration/cases/` — file case
  - `GET /api/v1/arbitration/cases/{id}/` — detail
  - `POST /api/v1/arbitration/cases/{id}/decide/` — render decision (IsLeaderAtTier)
  - `POST /api/v1/arbitration/cases/{id}/appeal/` — appeal to higher tier
  - **AC:** Full arbitration lifecycle works

- [ ] **GP-053** [P0] Endorsement fraud penalty workflow
  - When case_type='endorsement_fraud' and decision is guilty:
    - Suspend guarantor's endorsement rights (is_suspended=True)
    - Optionally reduce max_slots
    - Revoke the fraudulent endorsement
    - Revert supporter's role
  - **AC:** Penalty correctly propagates through endorsement and user models

- [-] **GP-054** [P0] Write tests for Phase 5 — DEFERRED

---

## Phase 6: Gamification & Polish (Weeks 16–18)

**Goal:** Progress tracking, caching, optimization, documentation.

### Sprint 6.1 — Gamification

- [ ] **GP-055** [P0] Gamification models
  - `TerritoryProgress` (precinct/district OneToOne, member counts, current_tier, members_for_next_tier)
  - `TierCapability` (tier, name, key, description)
  - **AC:** Models created

- [ ] **GP-056** [P0] `seed_tier_capabilities` management command
  - Seed default capabilities per tier:
    - Tier 10: basic_voting, sos_reporting
    - Tier 50: arbitration_basic, increased_visibility
    - Tier 100: tv_time, arbitration_advanced
    - Tier 1000: full_budget, council_membership
  - **AC:** Running command creates capability records

- [ ] **GP-057** [P0] Territory progress calculation
  - `update_territory_progress(precinct_id)` Celery task
  - Counts members, groups, determines current and next tier
  - Triggered by signals on Membership create/delete, Endorsement create/revoke
  - **AC:** Progress correctly calculated and cached in TerritoryProgress

- [ ] **GP-058** [P0] Gamification endpoints
  - `GET /api/v1/gamification/progress/` — user's territory progress with message
  - `GET /api/v1/gamification/progress/{precinct_id}/` — specific precinct
  - `GET /api/v1/gamification/capabilities/` — all capabilities by tier
  - `GET /api/v1/gamification/capabilities/unlocked/` — user's unlocked capabilities
  - **AC:** Endpoints return correct progress data and unlocked capabilities

### Sprint 6.2 — Optimization & Polish

- [ ] **GP-059** [P1] Redis caching layer
  - Cache territory data (1 hour TTL)
  - Cache gamification progress (5 min TTL, invalidate on membership change)
  - Cache election results after completion (indefinite)
  - Cache hierarchy tree (10 min TTL)
  - **AC:** Cache hits reduce DB queries. Invalidation works correctly.

- [ ] **GP-060** [P1] Query optimization
  - Audit all viewset querysets for N+1 problems
  - Add `select_related`/`prefetch_related` where needed
  - Ensure all filter fields are indexed
  - **AC:** No N+1 queries in common endpoints. Response times < 200ms for list endpoints.

- [ ] **GP-061** [P1] Django admin customization
  - Register all models with useful list_display, list_filter, search_fields
  - Bulk actions: import territories, manage elections, review SOS reports
  - **AC:** Admin panel is usable for operations team

- [ ] **GP-062** [P1] API documentation polish
  - Add descriptions to all drf-spectacular schema views
  - Add request/response examples
  - Group endpoints by tags
  - **AC:** Swagger UI has complete, readable documentation

- [ ] **GP-063** [P2] Notification framework stub
  - Abstract notification service (prepare for WebSocket/push)
  - In-app notification model (user, type, title, body, is_read, created_at)
  - `GET /api/v1/notifications/` endpoint
  - **AC:** Basic notification storage and retrieval works. Ready for push integration.

- [-] **GP-064** [P0] Write tests for Phase 6 — DEFERRED

- [ ] **GP-065** [P1] GeD periodic sync task
  - `sync_ged_data` Celery beat task (every 6 hours)
  - Re-fetch GeD data for all verified users from girchi.com
  - Update ged_balance, last_sync_at
  - Flag for admin review if GeD no longer valid (do not auto-revoke)
  - **AC:** Sync task runs, updates data, flags issues

---

## Cross-Cutting Concerns (Ongoing)

- [ ] **GP-100** [P1] Comprehensive error response format
  - Standardize error responses: `{"error": "code", "message": "...", "details": {...}}`
  - Custom exception handler in `common/exceptions.py`
  - **AC:** All error responses follow consistent format

- [ ] **GP-101** [P1] Request/response logging
  - Middleware for logging API requests (method, path, user, status, duration)
  - Exclude sensitive fields (password, JWT) from logs
  - **AC:** Logs written for all API requests in structured format

- [ ] **GP-102** [P2] API versioning strategy
  - URL-based versioning: `/api/v1/` (already in place)
  - Document versioning policy for future v2
  - **AC:** Versioned URL namespace configured

---

## Progress Summary

| Phase | Total Tasks | Done | Skipped | Remaining |
|-------|-------------|------|---------|-----------|
| Phase 1 | 14 | 12 | 2 (CI, tests) | 0 |
| Phase 2 | 10 | 4 (GeD, onboarding, permissions) | 1 (tests) | 5 |
| Phase 3 | 8 | 0 | 1 (tests) | 7 |
| Phase 4 | 11 | 0 | 1 (tests) | 10 |
| Phase 5 | 11 | 0 | 1 (tests) | 10 |
| Phase 6 | 11 | 0 | 1 (tests) | 10 |
| Cross-Cutting | 3 | 0 | 0 | 3 |
| **Total** | **68** | **16** | **6** | **45** |

---

## Dependency Graph

```
GP-004 (User model) ← everything depends on this                    ✅
GP-005 (JWT) ← all authenticated endpoints                         ✅
GP-008,009 (OTP) ← GP-017 (onboarding, needs IsPhoneVerified)      ✅
GP-015,016 (GeD) ← GP-028 (endorsement quota auto-created on GeD)  ✅ → next
GP-019 (territories) ← GP-025 (groups need precincts)              ⬜ → NEXT UP
GP-025,026 (groups) ← GP-033 (positions need groups)               ⬜
GP-028,029 (endorsement) ← GP-053 (arbitration fraud penalty)      ⬜
GP-033,034 (positions, elections) ← GP-037 (hierarchy elections)    ⬜
GP-025 (groups) + GP-033 (positions) ← GP-045 (SOS needs atistavi) ⬜
GP-057 (progress) ← GP-025 (groups), GP-028 (endorsements)         ⬜
```
