from rest_framework.throttling import SimpleRateThrottle


class OTPRateThrottle(SimpleRateThrottle):
    """Rate limit OTP requests: 5 per hour per phone number."""

    scope = "otp"

    def get_cache_key(self, request, view):
        phone = request.data.get("phone_number", "")
        if not phone:
            return None
        return self.cache_format % {
            "scope": self.scope,
            "ident": phone,
        }
