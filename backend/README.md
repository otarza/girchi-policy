# Girchi Digital Policy — Backend API

Django REST Framework backend for the Girchi Digital Policy platform.

## Tech Stack

- **Python** 3.12+
- **Django** 6.0
- **Django REST Framework** 3.16
- **PostgreSQL** 16
- **Redis** 7 (cache + Celery broker)
- **Celery** 5.6 (async tasks + periodic scheduling)
- **JWT** authentication (SimpleJWT)

## Quick Start (Docker)

The fastest way to get running. Requires [Docker Desktop](https://www.docker.com/products/docker-desktop/).

```bash
# 1. Clone and enter the backend directory
cd backend

# 2. Create your env file
cp .env.example .env

# 3. Start all services (PostgreSQL, Redis, Django, Celery worker, Celery beat)
docker-compose up -d

# 4. Run migrations
docker-compose exec web python manage.py migrate

# 5. Create a superuser (optional)
docker-compose exec web python manage.py createsuperuser
```

The API is now available at **http://localhost:8000/api/v1/**.

### Docker Services

| Service | Description | Port |
|---------|-------------|------|
| `web` | Django dev server | 8000 |
| `db` | PostgreSQL 16 | 5432 |
| `redis` | Redis 7 | 6379 |
| `celery_worker` | Celery task worker | — |
| `celery_beat` | Celery periodic scheduler | — |

### Useful Docker Commands

```bash
docker-compose logs web              # Django logs
docker-compose logs celery_worker    # Celery worker logs
docker-compose exec web python manage.py shell   # Django shell
docker-compose down                  # Stop all services
docker-compose down -v               # Stop and remove volumes (destroys DB data)
```

## Local Development (without Docker)

If you prefer running Django directly on your machine. Requires PostgreSQL and Redis running locally.

```bash
# 1. Create and activate virtual environment
python3.12 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements/dev.txt
pip install --no-deps -r requirements/nodeps.txt

# 3. Set up environment
cp .env.example .env
# Edit .env — DATABASE_URL and REDIS_URL should point to localhost

# 4. Run migrations
python manage.py migrate

# 5. Start the dev server
python manage.py runserver
```

> **Note:** `requirements/nodeps.txt` contains packages installed with `--no-deps` due to overly strict version caps (e.g., `django-celery-beat` caps `Django<6.0` but works fine with Django 6). Always install it separately with `--no-deps`.

## Project Structure

```
backend/
├── config/                 # Project configuration
│   ├── settings/           # Settings split by environment (base, dev, prod)
│   ├── urls.py             # Root URL config
│   ├── api_urls.py         # /api/v1/ routes
│   ├── celery.py           # Celery app config
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── accounts/           # Custom User model, JWT auth, registration, profile
│   └── verification/       # SMS OTP (smsoffice.ge), GeD verification, device fingerprinting
├── common/                 # Shared utilities
│   ├── permissions.py      # DRF permission classes
│   ├── validators.py       # Georgian phone & personal ID validators
│   ├── pagination.py
│   ├── mixins.py           # TimestampMixin, SoftDeleteMixin
│   └── throttling.py       # OTP rate throttle
├── requirements/
│   ├── base.txt            # Core dependencies
│   ├── dev.txt             # Dev/test tools (pytest, ruff, etc.)
│   ├── prod.txt            # Production (sentry, whitenoise, etc.)
│   └── nodeps.txt          # Packages requiring --no-deps install
├── docker-compose.yml
├── Dockerfile
└── manage.py
```

## API Endpoints

Base URL: `http://localhost:8000/api/v1/`

### Auth (`/api/v1/auth/`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/register/` | No | Register with phone number + password |
| POST | `/token/` | No | Get JWT access + refresh tokens |
| POST | `/token/refresh/` | No | Refresh access token |
| GET | `/me/` | JWT | Get own profile |
| PATCH | `/me/` | JWT | Update own profile |
| POST | `/me/onboarding/` | JWT | Submit onboarding data |

### Verification (`/api/v1/verification/`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/sms/send-otp/` | No | Send OTP to phone number |
| POST | `/sms/verify-otp/` | No | Verify OTP code |
| POST | `/ged/verify/` | JWT | Start GeD verification |
| GET | `/ged/status/` | JWT | Check GeD verification status |
| POST | `/device/fingerprint/` | JWT | Submit device fingerprint |

### API Docs

Interactive Swagger UI is available at **http://localhost:8000/api/docs/** when the server is running.

## Environment Variables

See `.env.example` for all available variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `DJANGO_SETTINGS_MODULE` | Settings module | `config.settings.dev` |
| `SECRET_KEY` | Django secret key | — |
| `DEBUG` | Debug mode | `True` |
| `DATABASE_URL` | PostgreSQL connection string | — |
| `REDIS_URL` | Redis connection string | — |
| `CELERY_BROKER_URL` | Celery broker URL | — |
| `SMS_API_KEY` | smsoffice.ge API key | — |
| `GIRCHI_API_BASE_URL` | girchi.com API base URL | — |

## Running Tests

```bash
# With Docker
docker-compose exec web pytest

# Local
pytest
```

## Linting

```bash
ruff check .          # Lint
ruff check . --fix    # Auto-fix
ruff format .         # Format
```

## Admin Panel

Django admin is available at **http://localhost:8000/admin/** after creating a superuser.
