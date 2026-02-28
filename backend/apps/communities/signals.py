from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.accounts.models import User
from .models import EndorsementQuota


@receiver(post_save, sender=User)
def create_endorsement_quota_for_geder(sender, instance, created, **kwargs):
    """
    Auto-create EndorsementQuota when user becomes GeDer.
    Triggered on User save if role is 'geder' and quota doesn't exist.
    """
    if instance.role == User.Role.GEDER:
        # Create quota if it doesn't exist
        EndorsementQuota.objects.get_or_create(
            geder=instance,
            defaults={
                "max_slots": 10,
                "used_slots": 0,
            },
        )
