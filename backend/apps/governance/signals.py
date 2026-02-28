from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.communities.models import GroupOfTen

from .models import GovernanceTier, LeaderPosition


@receiver(post_save, sender=GroupOfTen)
def create_atistavi_position_for_group(sender, instance, created, **kwargs):
    """
    Auto-create a tier=10 (Atistavi) LeaderPosition when a GroupOfTen is created.

    The position is initially vacant (holder=None) and will be filled via election.
    Uses get_or_create to ensure idempotency.
    """
    if created:
        LeaderPosition.objects.get_or_create(
            tier=GovernanceTier.ATISTAVI,
            group=instance,
            defaults={
                "precinct": instance.precinct,  # Set precinct for easier querying
                "holder": None,
                "is_active": True,
            },
        )
