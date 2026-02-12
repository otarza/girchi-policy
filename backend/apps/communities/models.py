from django.conf import settings
from django.db import models


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
