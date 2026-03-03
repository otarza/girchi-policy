from celery import shared_task


@shared_task(bind=True, max_retries=3)
def update_territory_progress(self, precinct_id):
    """
    Recalculate and persist TerritoryProgress for a precinct.

    Triggered by signals on Membership and Endorsement changes.
    Uses get_or_create so it is safe to call on precincts with no prior progress record.
    """
    from apps.communities.models import GroupOfTen, Membership
    from apps.gamification.models import TerritoryProgress

    try:
        member_count = (
            Membership.objects.filter(
                group__precinct_id=precinct_id,
                is_active=True,
            ).count()
        )
        group_count = GroupOfTen.objects.filter(precinct_id=precinct_id).count()

        progress, _ = TerritoryProgress.objects.get_or_create(precinct_id=precinct_id)
        progress.member_count = member_count
        progress.group_count = group_count
        progress.recalculate()
        progress.save()

        # Invalidate the cached progress for this precinct
        from django.core.cache import cache
        cache.delete(f"gamification:progress:{precinct_id}")

    except Exception as exc:
        raise self.retry(exc=exc, countdown=30)
