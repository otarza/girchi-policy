from django.contrib.auth.models import AbstractUser
from django.db import models

from common.validators import validate_georgian_personal_id, validate_georgian_phone

from .managers import UserManager


class User(AbstractUser):
    """
    Custom user model with phone_number as the primary identifier.
    Django 6: BigAutoField is the default PK — no need to set default_auto_field.
    Django 6: save() must use keyword arguments only.
    """

    username = None
    email = None

    class Role(models.TextChoices):
        UNVERIFIED = "unverified", "Unverified"
        GEDER = "geder", "GeDer"
        SUPPORTER = "supporter", "Endorsed Supporter"

    class MemberStatus(models.TextChoices):
        PASSIVE = "passive", "Passive Member"
        ACTIVE = "active", "Active Member"

    # Identity
    phone_number = models.CharField(
        max_length=20,
        unique=True,
        validators=[validate_georgian_phone],
    )
    personal_id_number = models.CharField(
        max_length=11,
        unique=True,
        null=True,
        blank=True,
        validators=[validate_georgian_personal_id],
    )

    # Role & Status
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.UNVERIFIED,
        db_index=True,
    )
    member_status = models.CharField(
        max_length=10,
        choices=MemberStatus.choices,
        default=MemberStatus.PASSIVE,
    )

    # Onboarding
    join_reason = models.TextField(blank=True)
    constitution_accepted = models.BooleanField(default=False)
    constitution_accepted_at = models.DateTimeField(null=True, blank=True)
    onboarding_completed = models.BooleanField(default=False)

    # Diaspora
    is_diaspora = models.BooleanField(default=False)

    # Territory assignment
    precinct = models.ForeignKey(
        "territories.Precinct",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )

    # Phone verification
    is_phone_verified = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        indexes = [
            models.Index(fields=["personal_id_number"]),
            models.Index(fields=["precinct", "role"]),
        ]

    def __str__(self):
        name = self.get_full_name() or self.phone_number
        return f"{name} ({self.role})"

    @property
    def is_council_member(self):
        """
        Check if user holds a tier=1000 (council) position.

        Council members (satatbiro) are users who hold thousand-leader positions.
        Returns True if user currently holds any active tier=1000 position.
        """
        from apps.governance.models import GovernanceTier

        return self.held_positions.filter(
            tier=GovernanceTier.THOUSAND, is_active=True
        ).exists()

    @classmethod
    def get_council_members(cls):
        """
        Return queryset of all users who hold tier=1000 (council) positions.

        Returns:
            QuerySet: Users who are council members (hold active tier=1000 positions)
        """
        from apps.governance.models import GovernanceTier

        return cls.objects.filter(
            held_positions__tier=GovernanceTier.THOUSAND,
            held_positions__is_active=True,
        ).distinct()


class Notification(models.Model):
    """
    In-app notification for a user.

    Stub for future WebSocket/push integration. Stores basic notification
    data that the mobile app can poll and mark as read.
    """

    class NotificationType(models.TextChoices):
        SOS = "sos", "SOS Update"
        ELECTION = "election", "Election"
        ENDORSEMENT = "endorsement", "Endorsement"
        INITIATIVE = "initiative", "Initiative"
        ARBITRATION = "arbitration", "Arbitration"
        SYSTEM = "system", "System"

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM,
        db_index=True,
    )
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read"]),
        ]

    def __str__(self):
        return f"[{self.type}] {self.title} → {self.user.phone_number}"
