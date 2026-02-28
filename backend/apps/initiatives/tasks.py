import logging

from celery import shared_task
from django.db.models import Count, F

logger = logging.getLogger(__name__)


@shared_task
def check_initiative_thresholds():
    """
    Detect initiatives that have reached their signature threshold.

    Periodic task (runs every 30 minutes via Celery Beat).

    Steps:
    1. Annotate all 'open' initiatives with their signature count
    2. Filter those where count >= threshold
    3. Bulk-update their status to 'threshold_met'
    4. Log results
    """
    from .models import Initiative

    open_initiatives = (
        Initiative.objects.filter(status=Initiative.Status.OPEN)
        .annotate(sig_count=Count("signatures"))
        .filter(sig_count__gte=F("signature_threshold"))
    )

    updated_ids = list(open_initiatives.values_list("id", flat=True))

    if updated_ids:
        Initiative.objects.filter(id__in=updated_ids).update(
            status=Initiative.Status.THRESHOLD_MET
        )
        logger.info(
            f"check_initiative_thresholds: {len(updated_ids)} initiatives "
            f"reached threshold: {updated_ids}"
        )
    else:
        logger.debug("check_initiative_thresholds: No initiatives reached threshold.")
