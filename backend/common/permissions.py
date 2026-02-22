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


class IsAtistavi(BasePermission):
    """
    User holds an atistavi (tier=10 leader) position.

    Used for:
    - SOS verification (only atistavis can verify local SOS reports)
    - Local group management
    - Actions requiring local leadership authority
    """

    message = "Must be an atistavi (10s leader) to perform this action."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Check if user holds any tier=10 position
        from apps.governance.models import GovernanceTier

        return request.user.held_positions.filter(
            tier=GovernanceTier.ATISTAVI, is_active=True
        ).exists()


class IsLeaderAtTier(BasePermission):
    """
    Parameterized permission: user holds position at or above specified tier.

    Usage:
        permission_classes = [IsAuthenticated, IsLeaderAtTier(50)]  # Fifty-leader or higher
        permission_classes = [IsAuthenticated, IsLeaderAtTier(100)]  # Hundred-leader or higher
        permission_classes = [IsAuthenticated, IsLeaderAtTier(1000)]  # Council member only

    Used for:
    - Election creation (may require tier=50+)
    - Arbitration decisions (may require tier=100+)
    - High-level governance actions
    """

    def __init__(self, min_tier=10):
        """
        Initialize with minimum required tier.

        Args:
            min_tier: Minimum governance tier (10, 50, 100, 1000)
        """
        self.min_tier = min_tier
        super().__init__()

    @property
    def message(self):
        """Dynamic message based on required tier."""
        tier_names = {
            10: "atistavi (10s leader)",
            50: "fifty-leader",
            100: "hundred-leader",
            1000: "council member (1000s leader)",
        }
        tier_name = tier_names.get(self.min_tier, f"tier {self.min_tier} leader")
        return f"Must be a {tier_name} or higher to perform this action."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Check if user holds any position at min_tier or higher
        from apps.governance.models import LeaderPosition

        return LeaderPosition.objects.filter(
            holder=request.user,
            tier__gte=self.min_tier,  # Greater than or equal
            is_active=True,
        ).exists()


# Convenience aliases for common tier requirements
class IsFiftyLeader(IsLeaderAtTier):
    """User holds fifty-leader (tier=50) or higher position."""

    def __init__(self):
        super().__init__(min_tier=50)


class IsHundredLeader(IsLeaderAtTier):
    """User holds hundred-leader (tier=100) or higher position."""

    def __init__(self):
        super().__init__(min_tier=100)


class IsCouncilMember(IsLeaderAtTier):
    """User holds council member (tier=1000) position."""

    def __init__(self):
        super().__init__(min_tier=1000)
