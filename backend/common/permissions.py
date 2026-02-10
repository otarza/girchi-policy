from rest_framework.permissions import BasePermission


class IsPhoneVerified(BasePermission):
    """User has completed SMS OTP verification."""

    message = "Phone number must be verified."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.is_phone_verified


class IsOnboarded(BasePermission):
    """User has completed the onboarding flow."""

    message = "Onboarding must be completed."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.onboarding_completed


class IsGeDer(BasePermission):
    """User has role == 'geder'."""

    message = "Must be a verified GeDer."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role == "geder"


class IsVerifiedMember(BasePermission):
    """User is either a GeDer or an endorsed supporter."""

    message = "Must be a verified member (GeDer or endorsed supporter)."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in ("geder", "supporter")


class IsActiveMember(BasePermission):
    """User must be an active member."""

    message = "Must be an active member."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.member_status == "active"


class IsNotDiaspora(BasePermission):
    """User is not in diaspora category."""

    message = "Diaspora members cannot participate in local governance."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return not request.user.is_diaspora
