# Girchi Digital Policy — Technical Specification

## 1. Overview

The Girchi Digital Policy application is a decentralized, self-governing platform where political decisions flow bottom-up through a hierarchical community structure. This document specifies the backend API architecture that serves both web and mobile clients.

### 1.1 Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | Django | 5.1+ |
| API | Django REST Framework (DRF) | 3.15+ |
| Database | PostgreSQL | 16 |
| Cache/Broker | Redis | 7 |
| Task Queue | Celery + django-celery-beat | 5.4+ |
| Auth | JWT (djangorestframework-simplejwt) | 5.3+ |
| API Docs | drf-spectacular (OpenAPI 3.0) | 0.27+ |
| Containerization | Docker + Docker Compose | latest |
| Python | 3.12+ | — |

### 1.2 External Integrations

| Service | Purpose | Protocol |
|---------|---------|----------|
| girchi.com (Strapi) | GeD verification & data sync | REST API, user JWT auth |
| smsoffice.ge | SMS OTP verification | REST API, API key auth |

---

## 2. Project Structure

```
girchi-policy/
├── docker-compose.yml
├── docker-compose.prod.yml
├── Dockerfile
├── .env.example
├── .gitignore
├── requirements/
│   ├── base.txt                   # Shared dependencies
│   ├── dev.txt                    # Dev/test tools (pytest, ruff, etc.)
│   └── prod.txt                   # Production (sentry, whitenoise, etc.)
├── manage.py
├── config/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py                # Common settings
│   │   ├── dev.py                 # DEBUG=True, local DB, CORS allow all
│   │   └── prod.py                # DEBUG=False, production DB, Sentry
│   ├── urls.py                    # Root URL config
│   ├── api_urls.py                # /api/v1/ namespace
│   ├── wsgi.py
│   ├── asgi.py
│   └── celery.py                  # Celery app config
├── apps/
│   ├── accounts/                  # User model, auth, registration, profile
│   │   ├── models.py
│   │   ├── managers.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── tests/
│   ├── verification/              # GeD, SMS/OTP, device fingerprinting
│   │   ├── models.py
│   │   ├── services.py            # SMSService, GeDService, DeviceFingerprintService
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── tasks.py               # Celery tasks
│   │   └── tests/
│   ├── territories/               # Regions, districts, precincts
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── management/
│   │   │   └── commands/
│   │   │       └── import_cec_data.py
│   │   └── tests/
│   ├── communities/               # Groups-of-10, endorsement, membership
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── signals.py             # Post-endorsement role promotion
│   │   ├── tasks.py
│   │   └── tests/
│   ├── governance/                # Elections, leader positions, hierarchy
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── services.py            # Election lifecycle, vote tallying
│   │   ├── tasks.py
│   │   └── tests/
│   ├── sos/                       # SOS reports and escalation
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── tasks.py               # Auto-assignment, timeout escalation
│   │   └── tests/
│   ├── initiatives/               # Petitions, initiatives, signatures
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── tasks.py
│   │   └── tests/
│   ├── arbitration/               # Dispute resolution, penalties
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests/
│   └── gamification/              # Progress tracking, tier capabilities
│       ├── models.py
│       ├── serializers.py
│       ├── views.py
│       ├── urls.py
│       ├── tasks.py
│       ├── management/
│       │   └── commands/
│       │       └── seed_tier_capabilities.py
│       └── tests/
└── common/
    ├── __init__.py
    ├── permissions.py             # DRF permission classes
    ├── pagination.py              # CursorPagination, PageNumberPagination
    ├── mixins.py                  # TimestampMixin, SoftDeleteMixin
    ├── validators.py              # Georgian personal ID, phone validators
    ├── exceptions.py              # Custom API exception handler
    ├── throttling.py              # OTP rate limiting
    └── utils.py
```

---

## 3. Data Models

### 3.1 `apps/accounts` — User & Authentication

#### User

| Field | Type | Constraints | Notes |
|-------|------|------------|-------|
| `phone_number` | CharField(20) | unique, indexed | `USERNAME_FIELD`, format: +995XXXXXXXXX |
| `personal_id_number` | CharField(11) | unique, nullable | Georgian personal number (11 digits) |
| `role` | CharField(20) | choices | `unverified` / `geder` / `supporter` |
| `member_status` | CharField(10) | choices | `passive` / `active` |
| `join_reason` | TextField | blank | "Why are you joining?" answer |
| `constitution_accepted` | BooleanField | default=False | Must be True to complete onboarding |
| `constitution_accepted_at` | DateTimeField | nullable | Timestamp of acceptance |
| `onboarding_completed` | BooleanField | default=False | True after Step 2 is done |
| `is_diaspora` | BooleanField | default=False | Excludes from local hierarchy |
| `precinct` | FK(Precinct) | nullable, SET_NULL | Territorial assignment |
| `created_at` | DateTimeField | auto_now_add | — |
| `updated_at` | DateTimeField | auto_now | — |

**Indexes:** `role`, `(precinct, role)`, `personal_id_number`

**Custom Manager:** `UserManager` with `create_user(phone_number, password)` and `create_superuser`.

### 3.2 `apps/verification` — External Integrations

#### SMSOTPRequest

| Field | Type | Constraints | Notes |
|-------|------|------------|-------|
| `phone_number` | CharField(20) | indexed | — |
| `code` | CharField(6) | — | 6-digit OTP code |
| `reference` | CharField(100) | blank | smsoffice.ge message reference |
| `is_verified` | BooleanField | default=False | — |
| `attempts` | PositiveSmallIntegerField | default=0 | Max 5 before lockout |
| `created_at` | DateTimeField | auto_now_add | — |
| `expires_at` | DateTimeField | — | created_at + 5 minutes |

#### GeDVerification

| Field | Type | Constraints | Notes |
|-------|------|------------|-------|
| `user` | OneToOne(User) | CASCADE | — |
| `ged_id` | CharField(100) | unique, nullable | GeD identifier from girchi.com |
| `girchi_user_id` | PositiveIntegerField | nullable | User ID on girchi.com |
| `is_verified` | BooleanField | default=False | — |
| `verified_at` | DateTimeField | nullable | — |
| `ged_balance` | DecimalField | nullable | GeD balance from last sync |
| `raw_response` | JSONField | default=dict | Last API response stored for audit |
| `last_sync_at` | DateTimeField | auto_now | — |

#### DeviceFingerprint

| Field | Type | Constraints | Notes |
|-------|------|------------|-------|
| `user` | FK(User) | CASCADE | Multiple devices per user |
| `fingerprint_hash` | CharField(255) | indexed | Hash of device signals |
| `device_data` | JSONField | default=dict | UA, screen, platform, etc. |
| `ip_address` | GenericIPAddressField | nullable | — |
| `is_flagged` | BooleanField | default=False | Suspicious device |
| `created_at` | DateTimeField | auto_now_add | — |

### 3.3 `apps/territories` — Electoral Geography

#### Region

| Field | Type | Constraints |
|-------|------|------------|
| `name` | CharField(200) | — |
| `name_ka` | CharField(200) | Georgian name |
| `code` | CharField(10) | unique |

#### District

| Field | Type | Constraints |
|-------|------|------------|
| `region` | FK(Region) | CASCADE |
| `name` | CharField(200) | — |
| `name_ka` | CharField(200) | — |
| `cec_code` | CharField(20) | unique |

#### Precinct

| Field | Type | Constraints |
|-------|------|------------|
| `district` | FK(District) | CASCADE |
| `name` | CharField(200) | — |
| `name_ka` | CharField(200) | — |
| `cec_code` | CharField(20) | unique |
| `latitude` | DecimalField(9,6) | nullable |
| `longitude` | DecimalField(9,6) | nullable |

### 3.4 `apps/communities` — Groups & Endorsement

#### GroupOfTen (ateuli)

| Field | Type | Constraints | Notes |
|-------|------|------------|-------|
| `precinct` | FK(Precinct) | CASCADE | — |
| `name` | CharField(200) | blank | Optional display name |
| `is_full` | BooleanField | default=False | True when ~10 members |
| `created_at` | DateTimeField | auto_now_add | — |

#### Membership

| Field | Type | Constraints |
|-------|------|------------|
| `user` | OneToOne(User) | CASCADE |
| `group` | FK(GroupOfTen) | CASCADE |
| `is_active` | BooleanField | default=True |
| `joined_at` | DateTimeField | auto_now_add |
| `left_at` | DateTimeField | nullable |

#### Endorsement

| Field | Type | Constraints | Notes |
|-------|------|------------|-------|
| `guarantor` | FK(User) | CASCADE | Must have role=geder |
| `supporter` | OneToOne(User) | CASCADE | The endorsed user |
| `status` | CharField(20) | choices | `active` / `revoked` / `penalized` |
| `created_at` | DateTimeField | auto_now_add | — |
| `revoked_at` | DateTimeField | nullable | — |
| `revoke_reason` | TextField | blank | — |

#### EndorsementQuota

| Field | Type | Constraints | Notes |
|-------|------|------------|-------|
| `geder` | OneToOne(User) | CASCADE | — |
| `max_slots` | PositiveSmallIntegerField | default=10 | Configurable per user |
| `used_slots` | PositiveSmallIntegerField | default=0 | — |
| `is_suspended` | BooleanField | default=False | Penalty: cannot endorse |
| `suspended_at` | DateTimeField | nullable | — |
| `suspended_reason` | TextField | blank | — |

### 3.5 `apps/governance` — Elections & Hierarchy

#### GovernanceTier (IntegerChoices)

| Value | Label |
|-------|-------|
| 10 | Atistavi (10s Leader) |
| 50 | 50s Leader |
| 100 | 100s Leader |
| 1000 | 1000s Leader (Council Member) |

#### LeaderPosition

| Field | Type | Constraints | Notes |
|-------|------|------------|-------|
| `tier` | IntegerField | GovernanceTier choices | — |
| `group` | OneToOne(GroupOfTen) | nullable, CASCADE | For tier=10 |
| `precinct` | FK(Precinct) | nullable, SET_NULL | For tier >= 50 |
| `district` | FK(District) | nullable, SET_NULL | For tier >= 100 |
| `holder` | FK(User) | nullable, SET_NULL | Current leader |
| `held_since` | DateTimeField | nullable | — |
| `parent` | FK(self) | nullable, SET_NULL | Hierarchy link |
| `is_active` | BooleanField | default=True | — |
| `created_at` | DateTimeField | auto_now_add | — |

**Hierarchy rules:**
- Tier 10 (Atistavi): linked to a GroupOfTen. Elected by group members (direct vote).
- Tier 50: 5 Atistavis elect one 50-leader from among themselves.
- Tier 100: 2 fifty-leaders elect one 100-leader from among themselves.
- Tier 1000: 10 hundred-leaders elect one 1000-leader from among themselves.
- Tier 1000 holders automatically become council (satatbiro) members.

#### Election

| Field | Type | Constraints |
|-------|------|------------|
| `election_type` | CharField(20) | `atistavi` / `hierarchy` / `parliamentary` |
| `status` | CharField(20) | `nomination` / `voting` / `completed` / `cancelled` |
| `position` | FK(LeaderPosition) | nullable (null for parliamentary) |
| `nomination_start` | DateTimeField | — |
| `nomination_end` | DateTimeField | — |
| `voting_start` | DateTimeField | — |
| `voting_end` | DateTimeField | — |
| `created_by` | FK(User) | nullable |
| `created_at` | DateTimeField | auto_now_add |

#### Candidacy

| Field | Type | Constraints |
|-------|------|------------|
| `election` | FK(Election) | CASCADE |
| `candidate` | FK(User) | CASCADE |
| `statement` | TextField | blank |
| `registered_at` | DateTimeField | auto_now_add |
| `is_approved` | BooleanField | default=True |

**Unique constraint:** `(election, candidate)`

#### Vote

| Field | Type | Constraints |
|-------|------|------------|
| `election` | FK(Election) | CASCADE |
| `voter` | FK(User) | CASCADE |
| `candidate` | FK(Candidacy) | CASCADE |
| `cast_at` | DateTimeField | auto_now_add |

**Unique constraint:** `(election, voter)` — one vote per election per user.

### 3.6 `apps/sos` — SOS Reports

#### SOSReport

| Field | Type | Constraints | Notes |
|-------|------|------------|-------|
| `reporter` | FK(User) | CASCADE | — |
| `status` | CharField(20) | choices | `pending` / `verified` / `escalated` / `resolved` / `rejected` |
| `escalation_level` | IntegerField | choices | 10 / 50 / 100 / 1000 / 9999 (media) |
| `title` | CharField(300) | — | — |
| `description` | TextField | — | — |
| `moral_filter_answer` | TextField | — | Answer to moral filter question |
| `assigned_to` | FK(User) | nullable, SET_NULL | Current handler |
| `created_at` | DateTimeField | auto_now_add | — |
| `updated_at` | DateTimeField | auto_now | — |
| `resolved_at` | DateTimeField | nullable | — |

#### SOSEscalation

| Field | Type | Constraints |
|-------|------|------------|
| `report` | FK(SOSReport) | CASCADE |
| `from_level` | IntegerField | EscalationLevel choices |
| `to_level` | IntegerField | EscalationLevel choices |
| `escalated_by` | FK(User) | nullable |
| `note` | TextField | blank |
| `created_at` | DateTimeField | auto_now_add |

### 3.7 `apps/initiatives` — Petitions

#### Initiative

| Field | Type | Constraints |
|-------|------|------------|
| `author` | FK(User) | CASCADE |
| `title` | CharField(300) | — |
| `description` | TextField | — |
| `status` | CharField(20) | `draft` / `open` / `threshold_met` / `responded` / `closed` |
| `precinct` | FK(Precinct) | nullable |
| `district` | FK(District) | nullable |
| `signature_threshold` | PositiveIntegerField | default=10 |
| `response_text` | TextField | blank |
| `responded_by` | FK(User) | nullable |
| `responded_at` | DateTimeField | nullable |
| `created_at` | DateTimeField | auto_now_add |

#### InitiativeSignature

| Field | Type | Constraints |
|-------|------|------------|
| `initiative` | FK(Initiative) | CASCADE |
| `signer` | FK(User) | CASCADE |
| `signed_at` | DateTimeField | auto_now_add |

**Unique constraint:** `(initiative, signer)`

### 3.8 `apps/arbitration` — Dispute Resolution

#### ArbitrationCase

| Field | Type | Constraints |
|-------|------|------------|
| `case_type` | CharField(30) | `member_dispute` / `endorsement_fraud` / `election_challenge` / `other` |
| `status` | CharField(20) | `submitted` / `under_review` / `hearing` / `decided` / `appealed` / `closed` |
| `complainant` | FK(User) | CASCADE |
| `respondent` | FK(User) | nullable |
| `title` | CharField(300) | — |
| `description` | TextField | — |
| `evidence` | JSONField | default=list |
| `arbitrator` | FK(User) | nullable |
| `tier` | IntegerField | GovernanceTier, default=50 |
| `decision_text` | TextField | blank |
| `decided_at` | DateTimeField | nullable |
| `related_endorsement` | FK(Endorsement) | nullable |
| `created_at` | DateTimeField | auto_now_add |

### 3.9 `apps/gamification` — Progress

#### TerritoryProgress

| Field | Type | Constraints | Notes |
|-------|------|------------|-------|
| `precinct` | OneToOne(Precinct) | nullable | One of precinct/district set |
| `district` | OneToOne(District) | nullable | — |
| `total_members` | PositiveIntegerField | default=0 | — |
| `total_geders` | PositiveIntegerField | default=0 | — |
| `total_supporters` | PositiveIntegerField | default=0 | — |
| `total_groups` | PositiveIntegerField | default=0 | — |
| `current_tier` | IntegerField | GovernanceTier | — |
| `members_for_next_tier` | PositiveIntegerField | default=0 | "7 more needed" |
| `next_tier` | IntegerField | nullable | — |
| `unlocked_capabilities` | JSONField | default=list | List of capability keys |
| `updated_at` | DateTimeField | auto_now | — |

#### TierCapability

| Field | Type | Constraints |
|-------|------|------------|
| `tier` | IntegerField | GovernanceTier |
| `name` | CharField(100) | — |
| `description` | TextField | — |
| `key` | CharField(50) | unique (e.g. `tv_time`, `arbitration`, `budget`) |

---

## 4. API Specification

All endpoints are prefixed with `/api/v1/`. Authentication is via JWT Bearer token unless noted.

### 4.1 Auth Endpoints (`/api/v1/auth/`)

#### `POST /register/`
Register a new user. No auth required.

**Request:**
```json
{
    "phone_number": "+995555123456",
    "personal_id_number": "01234567890",
    "password": "securepassword",
    "first_name": "Giorgi",
    "last_name": "Chkhikvadze"
}
```

**Response (201):**
```json
{
    "id": 1,
    "phone_number": "+995555123456",
    "role": "unverified",
    "member_status": "passive",
    "onboarding_completed": false
}
```

**Validations:**
- Phone number: Georgian format (+995XXXXXXXXX)
- Personal ID: 11 digits, unique across users
- Password: min 8 chars

#### `POST /token/`
JWT login. Returns access + refresh tokens.

**Request:**
```json
{
    "phone_number": "+995555123456",
    "password": "securepassword"
}
```

**Response (200):**
```json
{
    "access": "eyJ...",
    "refresh": "eyJ..."
}
```

#### `POST /token/refresh/`
Refresh access token.

#### `GET /me/`
Get current user profile. Requires auth.

**Response (200):**
```json
{
    "id": 1,
    "phone_number": "+995555123456",
    "personal_id_number": "01234567890",
    "first_name": "Giorgi",
    "last_name": "Chkhikvadze",
    "role": "geder",
    "member_status": "active",
    "is_diaspora": false,
    "onboarding_completed": true,
    "precinct": {
        "id": 42,
        "name_ka": "...ubani..."
    },
    "membership": {
        "group_id": 7,
        "group_name": "ათეული #7"
    },
    "held_positions": [
        {"tier": 10, "position_id": 12}
    ]
}
```

#### `PATCH /me/`
Update profile fields. Requires auth.

#### `POST /me/onboarding/`
Complete onboarding. Requires auth + phone verified.

**Request:**
```json
{
    "join_reason": "I want to build a better society",
    "member_status": "active",
    "constitution_accepted": true
}
```

**Permissions:** `IsPhoneVerified`

### 4.2 Verification Endpoints (`/api/v1/verification/`)

#### `POST /sms/send-otp/`
Send OTP to phone number. No auth required.

**Request:**
```json
{
    "phone_number": "+995555123456"
}
```

**Rate limit:** 5 requests per phone per hour.

#### `POST /sms/verify-otp/`
Verify OTP code. No auth required.

**Request:**
```json
{
    "phone_number": "+995555123456",
    "code": "123456"
}
```

**Response (200):**
```json
{
    "verified": true,
    "phone_number": "+995555123456"
}
```

#### `POST /ged/verify/`
Initiate GeD verification. Requires auth.

**Request:**
```json
{
    "girchi_jwt": "eyJ..."
}
```

The backend uses this JWT to call girchi.com API and verify GeD ownership. If verified, user role changes to `geder`.

**Response (200):**
```json
{
    "is_verified": true,
    "ged_id": "GED-12345",
    "ged_balance": 150.00
}
```

**Permissions:** `IsAuthenticated`

#### `GET /ged/status/`
Check GeD verification status.

#### `POST /device/fingerprint/`
Submit device fingerprint. Requires auth.

**Request:**
```json
{
    "fingerprint_hash": "abc123...",
    "device_data": {
        "user_agent": "...",
        "screen_resolution": "1080x2400",
        "platform": "Android"
    }
}
```

### 4.3 Territory Endpoints (`/api/v1/territories/`)

All read-only. Requires auth + onboarded.

#### `GET /regions/`
List all regions.

#### `GET /regions/{id}/districts/`
List districts in a region.

#### `GET /districts/{id}/precincts/`
List precincts in a district.

#### `GET /precincts/{id}/`
Precinct detail with member counts.

#### `GET /precincts/nearby/?lat=41.7&lng=44.8`
Find precincts near coordinates.

### 4.4 Community Endpoints (`/api/v1/communities/`)

#### `GET /groups/`
List groups in user's precinct (or specified precinct via `?precinct_id=`).

**Permissions:** `IsVerifiedMember`, `IsOnboarded`

#### `POST /groups/`
Create a new group-of-10 in user's precinct.

**Request:**
```json
{
    "name": "ათეული #1 - ვაკე"
}
```

**Permissions:** `IsGeDer`, `IsOnboarded`, `IsNotDiaspora`

#### `GET /groups/{id}/`
Group detail with member list.

#### `POST /groups/{id}/join/`
Join a group. GeDers join directly. Supporters need active endorsement first.

**Permissions:** `IsVerifiedMember`, `IsOnboarded`, `IsNotDiaspora`

#### `POST /groups/{id}/leave/`
Leave a group.

#### `POST /endorsements/`
Endorse a supporter (guarantor action).

**Request:**
```json
{
    "supporter_id": 42
}
```

**Permissions:** `IsGeDer`

**Business logic:**
- Checks quota: `endorsement_quota.remaining_slots > 0`
- Checks suspension: `endorsement_quota.is_suspended == False`
- Promotes supporter's role from `unverified` to `supporter`
- Increments `used_slots`

#### `DELETE /endorsements/{id}/`
Revoke endorsement.

**Business logic:**
- Reverts supporter's role to `unverified`
- Removes supporter from their group
- Decrements `used_slots`

#### `GET /endorsements/quota/`
Check own endorsement quota.

**Response (200):**
```json
{
    "max_slots": 10,
    "used_slots": 3,
    "remaining_slots": 7,
    "is_suspended": false
}
```

#### `GET /nearby-geders/?precinct_id=42`
List GeDers in a precinct who have endorsement slots available. Used by supporters to find guarantors.

**Permissions:** `IsAuthenticated`

### 4.5 Governance Endpoints (`/api/v1/governance/`)

#### `GET /positions/?tier=10&precinct_id=42`
List leader positions, filterable by tier and territory.

#### `GET /elections/?status=voting&election_type=atistavi`
List elections.

#### `POST /elections/`
Create election (authorized leaders or system-triggered).

**Request:**
```json
{
    "election_type": "atistavi",
    "position_id": 12,
    "nomination_start": "2026-03-01T00:00:00Z",
    "nomination_end": "2026-03-07T00:00:00Z",
    "voting_start": "2026-03-08T00:00:00Z",
    "voting_end": "2026-03-15T00:00:00Z"
}
```

**Permissions:** `IsLeaderAtTier(min_tier=50)` or `IsAdminUser`

#### `POST /elections/{id}/nominate/`
Register as candidate in an election.

**Request:**
```json
{
    "statement": "I will work for our community's growth"
}
```

**Permissions:** `IsActiveMember`, `IsNotDiaspora`

**Validation:** Election must be in `nomination` status.

#### `POST /elections/{id}/vote/`
Cast vote in an election.

**Request:**
```json
{
    "candidacy_id": 5
}
```

**Permissions:** `IsVerifiedMember`, `IsNotDiaspora`

**Validation:**
- Election must be in `voting` status.
- For `atistavi` elections: voter must be a member of the position's group.
- For `hierarchy` elections: voter must hold a position at the tier below.
- One vote per election enforced by unique constraint.

#### `GET /elections/{id}/results/`
Get vote tallies after election is completed.

**Response (200):**
```json
{
    "election_id": 1,
    "status": "completed",
    "winner": {"id": 5, "candidate_name": "Giorgi Chkhikvadze", "votes": 7},
    "results": [
        {"candidacy_id": 5, "candidate_name": "Giorgi Chkhikvadze", "votes": 7},
        {"candidacy_id": 6, "candidate_name": "Nino Beridze", "votes": 3}
    ],
    "total_votes": 10,
    "total_eligible_voters": 10
}
```

#### `GET /hierarchy/?district_id=5`
Full governance hierarchy tree for visualization.

**Response (200):**
```json
{
    "district": "District Name",
    "tree": {
        "tier": 1000,
        "holder": {"id": 1, "name": "..."},
        "children": [
            {
                "tier": 100,
                "holder": {"id": 2, "name": "..."},
                "children": [...]
            }
        ]
    }
}
```

### 4.6 SOS Endpoints (`/api/v1/sos/`)

#### `POST /reports/`
Create SOS report.

**Request:**
```json
{
    "title": "Unfair eviction from property",
    "description": "Details of the situation...",
    "moral_filter_answer": "Yes, I am an honest hardworking person..."
}
```

**Permissions:** `IsVerifiedMember`

**Auto-action:** Celery task assigns report to reporter's local Atistavi.

#### `GET /reports/`
List SOS reports. Returns own reports + reports assigned to user (if leader).

#### `POST /reports/{id}/verify/`
Atistavi verifies report as legitimate.

**Permissions:** `IsAtistavi` + must be assigned to report

#### `POST /reports/{id}/escalate/`
Escalate to next tier.

**Request:**
```json
{
    "note": "This requires attention from higher leadership"
}
```

**Business logic:** escalation_level goes 10→50→100→1000→9999(media). Report gets reassigned to the appropriate leader at the new level.

#### `POST /reports/{id}/resolve/`
Mark as resolved.

#### `POST /reports/{id}/reject/`
Reject as false report.

### 4.7 Initiative Endpoints (`/api/v1/initiatives/`)

#### `POST /`
Create initiative.

**Request:**
```json
{
    "title": "Build a new community library",
    "description": "Proposal details...",
    "precinct_id": 42,
    "signature_threshold": 25
}
```

**Permissions:** `IsVerifiedMember`

#### `POST /{id}/sign/`
Sign an initiative. One signature per user.

#### `DELETE /{id}/sign/`
Withdraw signature.

#### `POST /{id}/respond/`
Representative responds to threshold-met initiative.

**Request:**
```json
{
    "response_text": "We will organize a meeting to discuss this proposal..."
}
```

**Permissions:** `IsLeaderAtTier(min_tier=50)` for the initiative's territory

### 4.8 Arbitration Endpoints (`/api/v1/arbitration/`)

#### `POST /cases/`
File a new case.

**Request:**
```json
{
    "case_type": "endorsement_fraud",
    "respondent_id": 15,
    "title": "Fake endorsement report",
    "description": "Details...",
    "related_endorsement_id": 8
}
```

**Permissions:** `IsVerifiedMember`

#### `POST /cases/{id}/decide/`
Render decision.

**Request:**
```json
{
    "decision_text": "The endorsement is found to be fraudulent. Penalties applied.",
    "penalties": {
        "suspend_endorsement": true,
        "ged_penalty_amount": 10
    }
}
```

**Permissions:** `IsLeaderAtTier(min_tier=50)`

**Business logic (endorsement_fraud):**
- Suspends guarantor's endorsement rights (`is_suspended = True`)
- Records penalty
- Revokes the fraudulent endorsement
- Reverts supporter role

#### `POST /cases/{id}/appeal/`
Appeal to higher tier.

**Permissions:** Case complainant or respondent.

### 4.9 Gamification Endpoints (`/api/v1/gamification/`)

#### `GET /progress/`
Get progress for authenticated user's territory.

**Response (200):**
```json
{
    "precinct": "Precinct Name",
    "total_members": 43,
    "total_groups": 4,
    "current_tier": 10,
    "next_tier": 50,
    "members_for_next_tier": 7,
    "message": "Your precinct needs 7 more members to form a fifty",
    "unlocked_capabilities": ["basic_voting"]
}
```

#### `GET /capabilities/unlocked/`
List capabilities unlocked for user's territory.

---

## 5. Permission Classes

| Class | Condition | Used By |
|-------|-----------|---------|
| `IsPhoneVerified` | User completed SMS OTP | Onboarding |
| `IsOnboarded` | `onboarding_completed == True` | Most feature endpoints |
| `IsGeDer` | `role == 'geder'` | Endorsement, group creation |
| `IsVerifiedMember` | `role in ('geder', 'supporter')` | Voting, SOS, initiatives |
| `IsActiveMember` | `member_status == 'active'` | Candidacy registration |
| `IsAtistavi` | Holds tier=10 position | SOS verification |
| `IsLeaderAtTier(min_tier)` | Holds position >= min_tier | Election creation, arbitration |
| `IsNotDiaspora` | `is_diaspora == False` | All local governance |

---

## 6. External Integration Details

### 6.1 girchi.com API (GeD Verification)

**Base URLs:**
- Production: `https://admin.girchi.com`
- Development: `https://dev-admin.girchi.com`
- Local: `http://localhost:1337`

**Authentication:** User's girchi.com JWT Bearer token.

**Verification flow:**
1. User authenticates on girchi.com (separate flow)
2. User provides their girchi.com JWT to the policy app via `POST /api/v1/verification/ged/verify/`
3. Policy backend calls `GET {girchi_api}/api/users-permissions/users/{id}` with the JWT
4. If response confirms GeD ownership → create `GeDVerification` record, update user role to `geder`
5. Store `ged_balance` and `raw_response` for reference

**Periodic sync (Celery):**
- Task: `sync_ged_data` runs every 6 hours
- For each user with `GeDVerification.is_verified == True`:
  - Re-fetch user data from girchi.com
  - Update `ged_balance`, `last_sync_at`
  - If GeD no longer valid → flag for admin review (do not auto-revoke)

**Relevant girchi.com endpoints:**
- `GET /api/users-permissions/users/{id}` — user detail with GeD
- `GET /api/users-permissions/search-users?search={query}` — search users
- `GET /api/emitted-ged` — total emitted GeD stats
- `GET /api/ged-diff` — GeD changes
- `POST /api/auth/local/` — login (identifier + password)
- `POST /api/auth/local/register` — register (email, username, password, phone, displayName, personalID)

### 6.2 smsoffice.ge (SMS/OTP)

**API Docs:** https://smsoffice.ge/integration/

**Flow:**
1. Generate 6-digit OTP, store in `SMSOTPRequest` with 5-minute expiry
2. Send via smsoffice.ge API
3. User submits code → validate against stored record
4. Max 5 attempts per OTP
5. Rate limit: 5 OTP requests per phone per hour

---

## 7. Infrastructure Architecture

### 7.1 Docker Compose Services

```
┌─────────────────────────────────────────────┐
│                   NGINX                      │
│              (reverse proxy)                 │
└──────────────────┬──────────────────────────┘
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
┌─────────────────┐  ┌──────────────┐
│    Django Web    │  │  Static/Media│
│   (Gunicorn)    │  │  (WhiteNoise)│
│   port 8000     │  │              │
└────────┬────────┘  └──────────────┘
         │
    ┌────┴────┬──────────┐
    ▼         ▼          ▼
┌────────┐ ┌──────┐ ┌────────────┐
│PostgreSQL│ │Redis │ │   Celery   │
│  :5432  │ │:6379 │ │  Worker +  │
│         │ │      │ │    Beat    │
└─────────┘ └──────┘ └────────────┘
```

### 7.2 Redis Usage

| Purpose | DB | TTL |
|---------|-----|-----|
| Django cache | 0 | Varies per key |
| Celery broker | 1 | — |
| Rate limiting (throttle) | 2 | Auto-expire |

**Cache keys:**
- `territory:{id}:detail` — 1 hour
- `progress:{precinct_id}` — 5 minutes (invalidated on membership change)
- `hierarchy:{district_id}` — 10 minutes
- `election:{id}:results` — indefinite (after completion)
- `user:{id}:positions` — 2 minutes

### 7.3 Celery Tasks

**Async (fire-and-forget):**
- `send_otp_sms(phone_number, code)` — Send SMS via smsoffice.ge
- `verify_ged_async(user_id, girchi_jwt)` — Call girchi.com API
- `update_territory_progress(precinct_id)` — Recalculate gamification
- `tally_election_results(election_id)` — Count votes, assign winner
- `assign_sos_to_atistavi(report_id)` — Auto-assign SOS
- `notify_escalation(report_id, to_user_id)` — Notification on SOS escalation

**Periodic (celery-beat):**
- `sync_ged_data` — every 6 hours
- `close_expired_elections` — every 15 minutes
- `escalate_sos_timeout` — every 1 hour (escalate unhandled SOS after 24h)
- `check_initiative_thresholds` — every 30 minutes
- `cleanup_expired_otps` — every 1 hour (delete OTPs older than 24h)

### 7.4 Key Dependencies

```
# requirements/base.txt
Django>=5.1,<5.2
djangorestframework>=3.15,<3.16
djangorestframework-simplejwt>=5.3,<5.4
django-filter>=24.0
django-cors-headers>=4.3
django-redis>=5.4
django-environ>=0.11
django-celery-beat>=2.6
celery>=5.4
psycopg[binary]>=3.2
gunicorn>=22.0
requests>=2.32
drf-spectacular>=0.27

# requirements/dev.txt
-r base.txt
pytest>=8.0
pytest-django>=4.8
pytest-cov>=5.0
factory-boy>=3.3
ruff>=0.5
bandit>=1.7
django-debug-toolbar>=4.4

# requirements/prod.txt
-r base.txt
sentry-sdk[django]>=2.0
django-storages>=1.14
whitenoise>=6.7
```

---

## 8. Security Considerations

- **Phone number validation:** Strict +995 format, prevent international abuse
- **OTP brute-force:** Max 5 attempts per code, rate limit 5 codes/hour/phone
- **Device fingerprinting:** Flag accounts with matching fingerprints across different personal IDs
- **JWT tokens:** Short-lived access tokens (15 min), longer refresh tokens (7 days)
- **Personal data:** `personal_id_number` encrypted at rest (django-encrypted-model-fields or DB-level encryption)
- **Endorsement accountability:** Full audit trail on endorsements. Penalty system for fraud.
- **Vote secrecy:** Votes are stored with voter reference (not anonymous) per the spec — the system is transparent by design
- **Admin access:** Django admin requires 2FA (django-otp) in production
- **CORS:** Whitelist specific frontend domains in production

---

## 9. Deployment Strategy

### Development
```bash
docker compose up
# Django runs at http://localhost:8000
# PostgreSQL at localhost:5432
# Redis at localhost:6379
```

### Production
- Docker Compose or Kubernetes (cloud-agnostic)
- PostgreSQL: managed service (RDS, Cloud SQL, or self-hosted with backups)
- Redis: managed service or self-hosted
- Static files: WhiteNoise (or S3 + CloudFront if scale demands)
- Media files: S3-compatible storage (django-storages)
- SSL: Let's Encrypt via Nginx or cloud load balancer
- Monitoring: Sentry for errors, Prometheus/Grafana for metrics (optional at < 10K scale)
- Backups: Daily PostgreSQL pg_dump, stored off-site
