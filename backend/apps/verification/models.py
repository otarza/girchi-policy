from django.conf import settings
from django.db import models


class SMSOTPRequest(models.Model):
    """Tracks OTP codes sent via smsoffice.ge."""

    phone_number = models.CharField(max_length=20, db_index=True)
    code = models.CharField(max_length=6)
    reference = models.CharField(max_length=100, blank=True)
    is_verified = models.BooleanField(default=False)
    attempts = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=["phone_number", "is_verified"]),
            models.Index(fields=["expires_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        status = "verified" if self.is_verified else "pending"
        return f"OTP for {self.phone_number} ({status})"

    @property
    def is_expired(self):
        from django.utils import timezone

        return timezone.now() > self.expires_at


class GeDVerification(models.Model):
    """Records GeD API verification attempts and results."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ged_verification",
    )
    ged_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    girchi_user_id = models.PositiveIntegerField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    ged_balance = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    raw_response = models.JSONField(default=dict, blank=True)
    last_sync_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["ged_id"]),
        ]

    def __str__(self):
        status = "verified" if self.is_verified else "unverified"
        return f"GeD for {self.user} ({status})"


class DeviceFingerprint(models.Model):
    """Anti-fake: stores device identity signals per user."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="device_fingerprints",
    )
    fingerprint_hash = models.CharField(max_length=255, db_index=True)
    device_data = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    is_flagged = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["fingerprint_hash"]),
        ]

    def __str__(self):
        status = "FLAGGED" if self.is_flagged else "clean"
        return f"Device {self.fingerprint_hash[:12]}... ({status})"
