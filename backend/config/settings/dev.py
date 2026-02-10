"""
Development settings — Django 6.
"""

from datetime import timedelta

from .base import *  # noqa: F401, F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

# CORS: allow all in development
CORS_ALLOW_ALL_ORIGINS = True

# Debug toolbar
INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405
MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405
INTERNAL_IPS = ["127.0.0.1"]

# Console email backend
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Relaxed token lifetimes for development
SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"] = timedelta(hours=1)  # noqa: F405
SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"] = timedelta(days=30)  # noqa: F405
