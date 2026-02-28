from django.conf import settings
from django.db import models


class Endorsement(models.Model):
    """
    Endorsement relationship where a GeDer vouches for a supporter.
    GeDers can endorse up to their quota limit (default 10).
    If an endorsed user is fraudulent, the guarantor faces penalties.
    """

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        REVOKED = "revoked", "Revoked"
        PENALIZED = "penalized", "Penalized"

    guarantor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="endorsements_given",
        help_text="GeDer who vouches for the supporter",
    )
    supporter = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="endorsement",
        help_text="User being endorsed",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoke_reason = models.TextField(blank=True)

    class Meta:
        verbose_name = "Endorsement"
        verbose_name_plural = "Endorsements"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["guarantor", "status"]),
        ]

    def __str__(self):
        return f"{self.guarantor.phone_number} → {self.supporter.phone_number} ({self.status})"


class EndorsementQuota(models.Model):
    """
    Tracks a GeDer's endorsement capacity and usage.
    Automatically created when user becomes GeDer.
    Can be suspended as penalty for endorsing fraudulent users.
    """

    geder = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="endorsement_quota",
    )
    max_slots = models.PositiveSmallIntegerField(
        default=10, help_text="Maximum number of endorsements allowed"
    )
    used_slots = models.PositiveSmallIntegerField(
        default=0, help_text="Number of active endorsements"
    )
    is_suspended = models.BooleanField(
        default=False, help_text="Penalty: cannot endorse if suspended"
    )
    suspended_at = models.DateTimeField(null=True, blank=True)
    suspended_reason = models.TextField(blank=True)

    class Meta:
        verbose_name = "Endorsement Quota"
        verbose_name_plural = "Endorsement Quotas"

    def __str__(self):
        return f"{self.geder.phone_number}: {self.used_slots}/{self.max_slots}"

    @property
    def remaining_slots(self):
        """Calculate remaining endorsement capacity."""
        return max(0, self.max_slots - self.used_slots)

    @property
    def can_endorse(self):
        """Check if GeDer can endorse more users."""
        return not self.is_suspended and self.remaining_slots > 0


class GroupOfTen(models.Model):
    """
    Group of up to 10 members (ateuli) within a precinct.
    The basic unit of community organization.
    """

    precinct = models.ForeignKey(
        "territories.Precinct",
        on_delete=models.CASCADE,
        related_name="groups",
    )
    name = models.CharField(max_length=200, blank=True)
    is_full = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Group of Ten"
        verbose_name_plural = "Groups of Ten"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["precinct", "is_full"]),
        ]

    def __str__(self):
        display_name = self.name or f"Group #{self.id}"
        return f"{display_name} - {self.precinct.name}"

    @property
    def member_count(self):
        """Return the count of active members."""
        return self.members.filter(is_active=True).count()

    def update_full_status(self):
        """Update is_full based on active member count."""
        count = self.member_count
        self.is_full = count >= 10
        self.save(update_fields=["is_full"])


class Membership(models.Model):
    """
    Represents a user's membership in a group-of-ten.
    OneToOne with User ensures each user can only be in one group at a time.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="membership",
    )
    group = models.ForeignKey(
        GroupOfTen,
        on_delete=models.CASCADE,
        related_name="members",
    )
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Membership"
        verbose_name_plural = "Memberships"
        ordering = ["-joined_at"]
        indexes = [
            models.Index(fields=["group", "is_active"]),
        ]

    def __str__(self):
        return f"{self.user.phone_number} → {self.group}"
