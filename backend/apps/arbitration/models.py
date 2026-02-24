from django.conf import settings
from django.db import models


class ArbitrationCase(models.Model):
    """
    Formal dispute resolution case submitted by a verified member.

    Flow:
    1. Complainant files case (case_type auto-determines tier)
    2. Arbitrator (leader at appropriate tier) is assigned and reviews
    3. Arbitrator renders decision with optional penalties
    4. Parties may appeal within 7 days → tier promoted
    5. Auto-closes 7 days after decision if no appeal
    """

    class CaseType(models.TextChoices):
        MEMBER_DISPUTE = "member_dispute", "Member Dispute"
        ENDORSEMENT_FRAUD = "endorsement_fraud", "Endorsement Fraud"
        ELECTION_CHALLENGE = "election_challenge", "Election Challenge"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        SUBMITTED = "submitted", "Submitted"
        UNDER_REVIEW = "under_review", "Under Review"
        DECIDED = "decided", "Decided"
        APPEALED = "appealed", "Appealed"
        CLOSED = "closed", "Closed"

    # Tier choices mirror GovernanceTier but only 50+ handle arbitration
    ARBITRATION_TIER_CHOICES = [
        (50, "50s Leader"),
        (100, "100s Leader"),
        (1000, "1000s Leader (Council)"),
    ]

    case_type = models.CharField(
        max_length=30,
        choices=CaseType.choices,
        db_index=True,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SUBMITTED,
        db_index=True,
    )
    complainant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="arbitration_complaints",
    )
    respondent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="arbitration_responses",
    )
    title = models.CharField(max_length=300)
    description = models.TextField()
    evidence = models.JSONField(
        default=list,
        help_text='List of evidence items: [{"type": "text"|"file_url", "content": "..."}]',
    )
    arbitrator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="arbitration_cases",
        help_text="Leader assigned to adjudicate this case",
    )
    tier = models.IntegerField(
        choices=ARBITRATION_TIER_CHOICES,
        help_text="Governance tier responsible for adjudicating this case",
    )
    decision_text = models.TextField(blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    related_endorsement = models.ForeignKey(
        "communities.Endorsement",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="arbitration_cases",
        help_text="Relevant endorsement (for endorsement_fraud cases)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Arbitration Case"
        verbose_name_plural = "Arbitration Cases"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["complainant", "created_at"]),
            models.Index(fields=["arbitrator", "status"]),
            models.Index(fields=["status", "tier"]),
        ]

    def __str__(self):
        complainant_name = (
            self.complainant.get_full_name() or self.complainant.phone_number
        )
        return f"Case #{self.id}: {self.get_case_type_display()} by {complainant_name}"

    @property
    def next_appeal_tier(self):
        """Return the next tier for appeal, or None if at council."""
        tier_order = [50, 100, 1000]
        try:
            idx = tier_order.index(self.tier)
            if idx + 1 < len(tier_order):
                return tier_order[idx + 1]
        except ValueError:
            pass
        return None

    @property
    def can_appeal(self):
        """Check if the case can be appealed (decided + next tier exists)."""
        return self.status == self.Status.DECIDED and self.next_appeal_tier is not None

    @classmethod
    def get_initial_tier(cls, case_type: str) -> int:
        """Determine starting tier based on case type."""
        if case_type == cls.CaseType.ELECTION_CHALLENGE:
            return 100
        return 50
