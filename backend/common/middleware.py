import logging
import time

logger = logging.getLogger("girchi.api")

_SENSITIVE_FIELDS = frozenset({"password", "token", "access", "refresh", "code", "otp"})


class RequestLoggingMiddleware:
    """
    Logs every API request with method, path, user, status code, and duration.

    Sensitive fields (password, tokens, OTP codes) are never written to logs.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.monotonic()

        response = self.get_response(request)

        duration_ms = round((time.monotonic() - start) * 1000)
        user_id = request.user.pk if hasattr(request, "user") and request.user.is_authenticated else None

        logger.info(
            "%s %s %s %dms user=%s",
            request.method,
            request.path,
            response.status_code,
            duration_ms,
            user_id or "anon",
        )

        return response
