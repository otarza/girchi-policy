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
