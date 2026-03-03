"""
Base Django 6 settings for Girchi Policy project.
"""

from datetime import timedelta
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
env_file = BASE_DIR / ".env"
if env_file.exists():
    env.read_env(str(env_file))

# --- Security ---

SECRET_KEY = env("SECRET_KEY")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

# --- Apps ---

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "django_filters",
    "corsheaders",
    "django_celery_beat",
    "drf_spectacular",
]

LOCAL_APPS = [
    "apps.accounts",
    "apps.verification",
    "apps.territories",
    "apps.communities",
    "apps.governance",
    "apps.sos",
    "apps.initiatives",
    "apps.arbitration",
    "apps.gamification",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# --- Middleware ---

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "common.middleware.RequestLoggingMiddleware",
]

# --- URLs ---

ROOT_URLCONF = "config.urls"

# --- Templates ---

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# --- Database ---

DATABASES = {
    "default": env.db("DATABASE_URL", default="sqlite:///db.sqlite3"),
}

# --- Auth ---
# Django 6: DEFAULT_AUTO_FIELD defaults to BigAutoField — no need to set it.

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- i18n ---

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Tbilisi"
USE_I18N = True
USE_TZ = True

# --- Static files ---

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# --- DRF ---

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_PAGINATION_CLASS": "common.pagination.StandardPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "otp": "5/hour",
    },
    "EXCEPTION_HANDLER": "common.exceptions.custom_exception_handler",
}

# --- JWT ---

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=env.int("JWT_ACCESS_TOKEN_LIFETIME_MINUTES", default=15)
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=env.int("JWT_REFRESH_TOKEN_LIFETIME_DAYS", default=7)
    ),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": False,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# --- CORS ---

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])

# --- Redis / Cache ---

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL", default="redis://localhost:6379/0"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "girchi",
    }
}

# --- Celery ---

CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://localhost:6379/1")
CELERY_RESULT_BACKEND = env("CELERY_BROKER_URL", default="redis://localhost:6379/1")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

CELERY_BEAT_SCHEDULE = {
    # Governance: auto-transition elections every 15 minutes
    "close-expired-elections": {
        "task": "apps.governance.tasks.close_expired_elections",
        "schedule": 60 * 15,  # 15 minutes
    },
    # SOS: auto-escalate stale reports every hour
    "escalate-sos-timeout": {
        "task": "apps.sos.tasks.escalate_sos_timeout",
        "schedule": 60 * 60,  # 1 hour
    },
    # Initiatives: detect threshold-met initiatives every 30 minutes
    "check-initiative-thresholds": {
        "task": "apps.initiatives.tasks.check_initiative_thresholds",
        "schedule": 60 * 30,  # 30 minutes
    },
    # Arbitration: auto-close decided cases daily
    "auto-close-decided-cases": {
        "task": "apps.arbitration.tasks.auto_close_decided_cases",
        "schedule": 60 * 60 * 24,  # 24 hours
    },
    # Verification: re-sync GeD data every 6 hours
    "sync-ged-data": {
        "task": "apps.verification.tasks.sync_ged_data",
        "schedule": 60 * 60 * 6,  # 6 hours
    },
    # Verification: cleanup expired OTPs daily
    "cleanup-expired-otps": {
        "task": "apps.verification.tasks.cleanup_expired_otps",
        "schedule": 60 * 60 * 24,  # 24 hours
    },
}

# --- drf-spectacular ---

SPECTACULAR_SETTINGS = {
    "TITLE": "Girchi Digital Policy API",
    "DESCRIPTION": (
        "Backend API for the Girchi decentralized governance platform.\n\n"
        "**User flow:** Register → Verify phone (SMS OTP) → Verify GeD identity → Onboard → "
        "Join a group → Participate in elections, initiatives, and SOS reports.\n\n"
        "**Roles:** `unverified` → `geder` (GeD verified) or `supporter` (endorsed by a GeDer).\n\n"
        "**Auth:** All endpoints except registration and OTP use JWT Bearer tokens."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX": "/api/v1/",
    "TAGS": [
        {"name": "Auth", "description": "User registration, JWT tokens, profile, onboarding."},
        {"name": "Verification", "description": "SMS OTP, GeD identity verification, device fingerprinting."},
        {"name": "Territories", "description": "Georgian electoral geography: regions, districts, precincts."},
        {"name": "Communities", "description": "Groups of ten, endorsement system, nearby GeDers."},
        {"name": "Governance", "description": "Leadership positions, elections, voting, hierarchy tree."},
        {"name": "SOS", "description": "Crisis reporting, local verification, escalation chain."},
        {"name": "Initiatives", "description": "Community petitions, signatures, threshold detection, leader responses."},
        {"name": "Arbitration", "description": "Dispute resolution, case lifecycle, appeal chain."},
        {"name": "Gamification", "description": "Territory progress, tier capabilities, unlocked features."},
        {"name": "Notifications", "description": "In-app notification inbox."},
    ],
    "COMPONENT_SPLIT_REQUEST": True,
}

# --- SMS (smsoffice.ge) ---

SMS_API_KEY = env("SMS_API_KEY", default="")
SMS_SENDER = env("SMS_SENDER", default="Girchi")

# --- GeD (girchi.com) ---

GIRCHI_API_BASE_URL = env("GIRCHI_API_BASE_URL", default="https://dev-admin.girchi.com")
