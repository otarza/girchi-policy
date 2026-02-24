from django.conf import settings
from django.db import models


class EscalationLevel(models.IntegerChoices):
    """
    Escalation levels in the SOS chain.
    Maps directly to governance tiers plus media escalation.
    """

    ATISTAVI = 10, "Atistavi (Group Leader)"
    FIFTY = 50, "50s Leader"
    HUNDRED = 100, "100s Leader"
    THOUSAND = 1000, "1000s Leader (Council)"
    MEDIA = 9999, "Media"

    @classmethod
    def next_level(cls, current_level: int):
        """Return the next escalation level, or None if already at media."""
        ordered = [10, 50, 100, 1000, 9999]
        try:
            idx = ordered.index(current_level)
            if idx + 1 < len(ordered):
                return ordered[idx + 1]
        except ValueError:
            pass
        return None


class SOSReport(models.Model):
    """
    Crisis report submitted by a verified member.

    Flow:
    1. Reporter submits with moral_filter_answer
    2. Celery task auto-assigns to reporter's Atistavi
    3. Atistavi verifies or rejects
    4. If verified, can be escalated up the chain or resolved
    5. Auto-escalates if no action taken in 24h
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        VERIFIED = "verified", "Verified"
        ESCALATED = "escalated", "Escalated"
        RESOLVED = "resolved", "Resolved"
        REJECTED = "rejected", "Rejected"

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sos_reports",
        help_text="User who submitted the SOS report",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    escalation_level = models.IntegerField(
        choices=EscalationLevel.choices,
        default=EscalationLevel.ATISTAVI,
        db_index=True,
        help_text="Current escalation level (which governance tier is handling this)",
    )
    title = models.CharField(max_length=300)
    description = models.TextField()
    moral_filter_answer = models.TextField(
        help_text="Reporter's answer to the moral filter question"
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_sos_reports",
        help_text="Leader currently handling this report",
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "SOS Report"
        verbose_name_plural = "SOS Reports"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["assigned_to", "status"]),
            models.Index(fields=["reporter", "created_at"]),
            models.Index(fields=["escalation_level"]),
        ]

    def __str__(self):
        reporter_name = self.reporter.get_full_name() or self.reporter.phone_number
        return f"SOS #{self.id} by {reporter_name} - {self.get_status_display()}"

    def get_next_escalation_level(self):
        """Return next escalation level value, or None if at media."""
        return EscalationLevel.next_level(self.escalation_level)

    def find_leader_at_next_level(self):
        """
        Find the appropriate leader user at the next escalation level
        based on reporter's territory.

        Returns:
            User or None: Leader user to assign to, or None for media level.
        """
        next_level = self.get_next_escalation_level()
        if next_level is None or next_level == EscalationLevel.MEDIA:
            return None

        from apps.governance.models import GovernanceTier, LeaderPosition

        reporter = self.reporter

        if next_level == EscalationLevel.FIFTY:
            # Find fifty-leader in reporter's precinct
            position = LeaderPosition.objects.filter(
                tier=GovernanceTier.FIFTY,
                precinct=reporter.precinct,
                is_active=True,
                holder__isnull=False,
            ).first()

        elif next_level == EscalationLevel.HUNDRED:
            # Find hundred-leader in reporter's district
            precinct = reporter.precinct
            if precinct:
                position = LeaderPosition.objects.filter(
                    tier=GovernanceTier.HUNDRED,
                    district=precinct.district,
                    is_active=True,
                    holder__isnull=False,
                ).first()
            else:
                position = None

        elif next_level == EscalationLevel.THOUSAND:
            # Find any active thousand-leader (council member)
            position = LeaderPosition.objects.filter(
                tier=GovernanceTier.THOUSAND,
                is_active=True,
                holder__isnull=False,
            ).first()

        else:
            position = None

        return position.holder if position else None


class SOSEscalation(models.Model):
    """
    Audit record of each escalation step in an SOS report's lifecycle.
    escalated_by=None indicates auto-escalation due to handler inactivity.
    """

    report = models.ForeignKey(
        SOSReport,
        on_delete=models.CASCADE,
        related_name="escalations",
    )
    from_level = models.IntegerField(choices=EscalationLevel.choices)
    to_level = models.IntegerField(choices=EscalationLevel.choices)
    escalated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sos_escalations_performed",
        help_text="User who escalated. Null = auto-escalated by system.",
    )
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "SOS Escalation"
        verbose_name_plural = "SOS Escalations"
        ordering = ["created_at"]

    def __str__(self):
        who = self.escalated_by.phone_number if self.escalated_by else "System"
        return f"SOS #{self.report_id}: {self.from_level} → {self.to_level} by {who}"
