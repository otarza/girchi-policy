import logging

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def apply_endorsement_penalties(case_id: int):
    """
    Apply penalties for a decided endorsement fraud case.

    Steps:
    1. Get the case and its related endorsement
    2. Revoke the endorsement
    3. Suspend guarantor's EndorsementQuota
    4. Revert supporter's role to 'unverified'
    5. Deactivate supporter's group membership

    Called after a decision on an 'endorsement_fraud' case.
    """
    from apps.communities.models import Endorsement, EndorsementQuota, Membership

    from .models import ArbitrationCase

    try:
        case = ArbitrationCase.objects.select_related(
            "related_endorsement__guarantor",
            "related_endorsement__supporter",
        ).get(id=case_id)
    except ArbitrationCase.DoesNotExist:
        logger.error(f"ArbitrationCase {case_id} does not exist")
        return

    endorsement = case.related_endorsement
    if not endorsement:
        logger.warning(f"Case {case_id} has no related endorsement. No penalties applied.")
        return

    guarantor = endorsement.guarantor
    supporter = endorsement.supporter

    # 1. Revoke the endorsement
    endorsement.status = Endorsement.Status.PENALIZED
    endorsement.save(update_fields=["status"])

    # 2. Suspend guarantor's endorsement quota
    EndorsementQuota.objects.filter(geder=guarantor).update(
        is_suspended=True,
        suspended_at=timezone.now(),
        suspended_reason=f"Arbitration case #{case_id} — fraudulent endorsement.",
    )

    # 3. Revert supporter role to 'unverified'
    supporter.role = "unverified"
    supporter.save(update_fields=["role"])

    # 4. Deactivate supporter's group membership
    Membership.objects.filter(user=supporter, is_active=True).update(
        is_active=False,
        left_at=timezone.now(),
    )

    logger.info(
        f"Endorsement fraud penalties applied for Case #{case_id}: "
        f"Endorsement #{endorsement.id} penalized, "
        f"Guarantor {guarantor.id} quota suspended, "
        f"Supporter {supporter.id} reverted to unverified."
    )


@shared_task
def auto_close_decided_cases():
    """
    Auto-close arbitration cases that have been decided for 7+ days with no appeal.

    Periodic task (runs daily via Celery Beat).
    """
    from .models import ArbitrationCase

    cutoff = timezone.now() - timezone.timedelta(days=7)

    cases_to_close = ArbitrationCase.objects.filter(
        status=ArbitrationCase.Status.DECIDED,
        decided_at__lte=cutoff,
    )

    count = cases_to_close.count()
    cases_to_close.update(status=ArbitrationCase.Status.CLOSED)

    logger.info(f"auto_close_decided_cases: {count} cases closed.")
