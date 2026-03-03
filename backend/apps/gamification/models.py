from django.db import models

from apps.territories.models import Precinct

# Tier thresholds: how many members a precinct needs to reach each tier.
TIER_THRESHOLDS = [
    (10, 10),    # Tier 10: 10 members (1 group of ten)
    (50, 50),    # Tier 50: 50 members
    (100, 100),  # Tier 100: 100 members
    (1000, 500), # Tier 1000: 500 members (full council eligibility)
]


def _current_tier(member_count):
    """Return the highest unlocked tier for a given member count."""
    current = 0
    for tier, threshold in TIER_THRESHOLDS:
        if member_count >= threshold:
            current = tier
    return current


def _members_for_next_tier(member_count):
    """Return how many more members are needed to unlock the next tier (None if maxed)."""
    for tier, threshold in TIER_THRESHOLDS:
        if member_count < threshold:
            return threshold - member_count
    return None


class TerritoryProgress(models.Model):
    """
    Cached progress snapshot for a precinct.

    Updated asynchronously by update_territory_progress Celery task whenever
    memberships or endorsements change.
    """

    precinct = models.OneToOneField(
        Precinct,
        on_delete=models.CASCADE,
        related_name="progress",
    )
    member_count = models.PositiveIntegerField(default=0)
    group_count = models.PositiveIntegerField(default=0)
    current_tier = models.IntegerField(default=0)
    members_for_next_tier = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Territory Progress"
        verbose_name_plural = "Territory Progress"

    def __str__(self):
        return f"{self.precinct} — tier {self.current_tier} ({self.member_count} members)"

    def recalculate(self):
        """Recompute tier fields from current member_count (call after updating member_count)."""
        self.current_tier = _current_tier(self.member_count)
        self.members_for_next_tier = _members_for_next_tier(self.member_count)


class TierCapability(models.Model):
    """
    A named capability that becomes available to a precinct at a specific tier.

    Seeded via: python manage.py seed_tier_capabilities
    """

    tier = models.IntegerField(
        help_text="Governance tier at which this capability is unlocked (10, 50, 100, 1000)."
    )
    name = models.CharField(max_length=100)
    key = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["tier", "key"]
        verbose_name = "Tier Capability"
        verbose_name_plural = "Tier Capabilities"

    def __str__(self):
        return f"[Tier {self.tier}] {self.name}"
