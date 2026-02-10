"""
Production settings — Django 6.
"""

from .base import *  # noqa: F401, F403

DEBUG = False

# --- Security ---

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Django 6 CSP — basic policy for admin-only HTML
SECURE_CSP = {
    "default-src": ["'self'"],
    "script-src": ["'self'"],
    "style-src": ["'self'", "'unsafe-inline'"],
    "img-src": ["'self'", "data:"],
}

# --- Static files ---

MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa: F405
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# --- Sentry ---

import sentry_sdk  # noqa: E402

sentry_sdk.init(
    dsn=env("SENTRY_DSN", default=""),  # noqa: F405
    traces_sample_rate=0.1,
)
