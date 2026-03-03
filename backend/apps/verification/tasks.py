import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def send_otp_sms(phone_number: str):
    """Send OTP via SMS asynchronously."""
    from .services import SMSService

    sms_service = SMSService()
    sms_service.send_otp(phone_number)


@shared_task
def cleanup_expired_otps():
    """Delete OTP records older than 24 hours."""
    from .models import SMSOTPRequest

    cutoff = timezone.now() - timedelta(hours=24)
    deleted_count, _ = SMSOTPRequest.objects.filter(created_at__lt=cutoff).delete()
    logger.info("Cleaned up %d expired OTP records", deleted_count)


@shared_task
def sync_ged_data():
    """
    Re-sync GeD data for all verified users from girchi.com every 6 hours.

    Updates ged_balance and last_sync_at for each verified user.
    Flags (but does NOT auto-revoke) users whose GeD is no longer valid.
    Admin must manually review flagged users.
    """
    from django.contrib.auth import get_user_model

    from .models import GeDVerification
    from .services import GeDService

    User = get_user_model()
    service = GeDService()

    verifications = GeDVerification.objects.filter(is_verified=True).select_related("user")
    synced = 0
    flagged = 0

    for verification in verifications:
        try:
            # Re-fetch using the stored girchi user ID (no JWT re-auth needed for admin endpoint)
            is_valid, data = service.verify_user_by_id(verification.girchi_user_id)

            if is_valid:
                verification.ged_balance = data.get("ged_balance", verification.ged_balance)
                verification.last_sync_at = timezone.now()
                verification.save(update_fields=["ged_balance", "last_sync_at"])
                synced += 1
            else:
                # Flag for admin review — do NOT auto-revoke
                verification.last_sync_at = timezone.now()
                verification.save(update_fields=["last_sync_at"])
                logger.warning(
                    "GeD sync: user %s (ged_id=%s) no longer valid — flagged for review",
                    verification.user.phone_number,
                    verification.ged_id,
                )
                flagged += 1

        except Exception:
            logger.exception(
                "GeD sync: failed to sync user %s", verification.user.phone_number
            )

    logger.info("GeD sync complete. Synced: %d, Flagged: %d", synced, flagged)
