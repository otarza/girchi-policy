"""
Signals that trigger territory progress recalculation.

Wired to:
- Membership post_save / post_delete
- Endorsement post_save (status changes)
"""

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver


@receiver(post_save, sender="communities.Membership")
def membership_changed(sender, instance, **kwargs):
    """Recalculate progress whenever a membership is saved (join or leave)."""
    precinct_id = instance.group.precinct_id
    if precinct_id:
        from apps.gamification.tasks import update_territory_progress
        update_territory_progress.delay(precinct_id)


@receiver(post_delete, sender="communities.Membership")
def membership_deleted(sender, instance, **kwargs):
    """Recalculate progress when a membership row is hard-deleted."""
    precinct_id = instance.group.precinct_id
    if precinct_id:
        from apps.gamification.tasks import update_territory_progress
        update_territory_progress.delay(precinct_id)


@receiver(post_save, sender="communities.Endorsement")
def endorsement_changed(sender, instance, **kwargs):
    """Recalculate progress for the supporter's precinct on endorsement changes."""
    precinct_id = getattr(instance.supporter, "precinct_id", None)
    if precinct_id:
        from apps.gamification.tasks import update_territory_progress
        update_territory_progress.delay(precinct_id)
