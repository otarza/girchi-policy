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
