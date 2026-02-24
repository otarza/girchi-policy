import logging

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def assign_sos_to_atistavi(report_id: int):
    """
    Auto-assign an SOS report to the reporter's group atistavi.

    Steps:
    1. Get reporter's active Membership → GroupOfTen
    2. Find active Atistavi (tier=10 LeaderPosition) for that group
    3. Assign report.assigned_to = atistavi.holder
    4. If no Atistavi found, leave assigned_to=None (admin handles)
    """
    from apps.governance.models import GovernanceTier, LeaderPosition

    from .models import SOSReport

    try:
        report = SOSReport.objects.select_related(
            "reporter__membership__group"
        ).get(id=report_id)
    except SOSReport.DoesNotExist:
        logger.error(f"SOSReport {report_id} does not exist")
        return

    reporter = report.reporter

    # Find reporter's group via membership
    try:
        membership = reporter.membership
        group = membership.group if membership.is_active else None
    except Exception:
        group = None

    if not group:
        logger.warning(
            f"SOS #{report_id}: Reporter {reporter.id} has no active group membership. "
            "Cannot auto-assign."
        )
        return

    # Find atistavi for this group
    position = LeaderPosition.objects.filter(
        tier=GovernanceTier.ATISTAVI,
        group=group,
        is_active=True,
        holder__isnull=False,
    ).first()

    if not position:
        logger.warning(
            f"SOS #{report_id}: No atistavi found for group {group.id}. "
            "Report remains unassigned."
        )
        return

    report.assigned_to = position.holder
    report.save(update_fields=["assigned_to", "updated_at"])

    logger.info(
        f"SOS #{report_id} assigned to atistavi {position.holder.id} "
        f"({position.holder.phone_number}) for group {group.id}"
    )


@shared_task
def escalate_sos_timeout():
    """
    Auto-escalate SOS reports that have been inactive for 24+ hours.

    Periodic task (runs every 1 hour via Celery Beat).

    Steps:
    1. Find reports in 'pending' or 'verified' status not updated in 24h
    2. For each: perform escalation to next level
    3. Create SOSEscalation record with escalated_by=None (system)
    4. Log the action
    """
    from .models import EscalationLevel, SOSEscalation, SOSReport

    cutoff = timezone.now() - timezone.timedelta(hours=24)

    stale_reports = SOSReport.objects.filter(
        status__in=[SOSReport.Status.PENDING, SOSReport.Status.VERIFIED],
        updated_at__lte=cutoff,
    ).select_related("reporter__precinct__district")

    escalated_count = 0

    for report in stale_reports:
        next_level = report.get_next_escalation_level()

        if next_level is None:
            # Already at media level — cannot escalate further
            continue

        from_level = report.escalation_level
        new_leader = report.find_leader_at_next_level()

        # Update report
        report.escalation_level = next_level
        report.status = SOSReport.Status.ESCALATED
        report.assigned_to = new_leader  # May be None at media level
        report.save(update_fields=["escalation_level", "status", "assigned_to", "updated_at"])

        # Create escalation audit record
        SOSEscalation.objects.create(
            report=report,
            from_level=from_level,
            to_level=next_level,
            escalated_by=None,  # System auto-escalation
            note="Auto-escalated due to handler inactivity (24h timeout).",
        )

        escalated_count += 1
        logger.info(
            f"SOS #{report.id} auto-escalated: {from_level} → {next_level}"
        )

    logger.info(f"SOS timeout escalation: {escalated_count} reports escalated.")
