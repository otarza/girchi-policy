import logging

from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import (
    AuthenticationFailed,
    MethodNotAllowed,
    NotAuthenticated,
    NotFound,
    PermissionDenied as DRFPermissionDenied,
    Throttled,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom DRF exception handler.

    Returns a consistent error format:
        {
            "error": "SNAKE_CASE_CODE",
            "message": "Human-readable message",
            "details": { ... }   # optional, present on validation errors
        }
    """
    # Map Django exceptions to DRF equivalents
    if isinstance(exc, Http404):
        exc = NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = DRFPermissionDenied()

    response = drf_exception_handler(exc, context)

    if response is None:
        logger.exception("Unhandled exception", exc_info=exc)
        return Response(
            {
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred.",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    error_code, message, details = _extract_error_info(exc, response)

    payload = {"error": error_code, "message": message}
    if details:
        payload["details"] = details

    response.data = payload
    return response


def _extract_error_info(exc, response):
    """Extract (error_code, message, details) from a DRF exception."""
    if isinstance(exc, ValidationError):
        details = response.data if isinstance(response.data, dict) else {"non_field_errors": response.data}
        # Flatten single-field errors for a cleaner message
        first_message = _first_message(details)
        return "VALIDATION_ERROR", first_message, details

    if isinstance(exc, NotAuthenticated) or isinstance(exc, AuthenticationFailed):
        return "AUTHENTICATION_REQUIRED", str(exc.detail), None

    if isinstance(exc, DRFPermissionDenied):
        return "PERMISSION_DENIED", str(exc.detail), None

    if isinstance(exc, NotFound):
        return "NOT_FOUND", str(exc.detail), None

    if isinstance(exc, MethodNotAllowed):
        return "METHOD_NOT_ALLOWED", str(exc.detail), None

    if isinstance(exc, Throttled):
        details = {"wait_seconds": exc.wait} if exc.wait else None
        return "THROTTLED", "Request was throttled. Please slow down.", details

    # Fallback for other DRF exceptions
    detail = response.data.get("detail") if isinstance(response.data, dict) else response.data
    return "ERROR", str(detail) if detail else "An error occurred.", None


def _first_message(details):
    """Extract the first human-readable message from a validation error dict."""
    for value in details.values():
        if isinstance(value, list) and value:
            item = value[0]
            return str(item)
        if isinstance(value, str):
            return value
    return "Validation failed."
