from django.conf import settings
from django.db import models


class Initiative(models.Model):
    """
    Community initiative / petition submitted by a verified member.

    Flow:
    1. Author creates initiative with title, description, target territory, threshold
    2. Starts in 'open' status immediately
    3. Verified members in territory sign
    4. Periodic task detects when signatures >= threshold → 'threshold_met'
    5. Territory leader (tier >= 50) provides official response → 'responded'
    """

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        THRESHOLD_MET = "threshold_met", "Threshold Met"
        RESPONDED = "responded", "Responded"
        CLOSED = "closed", "Closed"

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="initiatives",
    )
    title = models.CharField(max_length=300)
    description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True,
    )

    # Territory (at least one must be set)
    precinct = models.ForeignKey(
        "territories.Precinct",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="initiatives",
    )
    district = models.ForeignKey(
        "territories.District",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="initiatives",
    )

    signature_threshold = models.PositiveIntegerField(
        default=10,
        help_text="Number of signatures required to meet the threshold",
    )

    # Response from representative
    response_text = models.TextField(blank=True)
    responded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="initiative_responses",
    )
    responded_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Initiative"
        verbose_name_plural = "Initiatives"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "precinct"]),
            models.Index(fields=["author", "created_at"]),
        ]

    def __str__(self):
        return f"Initiative #{self.id}: {self.title[:60]}"

    @property
    def signature_count(self):
        """Return total signature count."""
        return self.signatures.count()


class InitiativeSignature(models.Model):
    """
    A verified member's signature on an initiative.
    Each user can sign a given initiative only once.
    """

    initiative = models.ForeignKey(
        Initiative,
        on_delete=models.CASCADE,
        related_name="signatures",
    )
    signer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="initiative_signatures",
    )
    signed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Initiative Signature"
        verbose_name_plural = "Initiative Signatures"
        ordering = ["-signed_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["initiative", "signer"],
                name="unique_signature_per_user_per_initiative",
            )
        ]
        indexes = [
            models.Index(fields=["initiative", "signed_at"]),
        ]

    def __str__(self):
        return f"{self.signer.phone_number} signed Initiative #{self.initiative_id}"
