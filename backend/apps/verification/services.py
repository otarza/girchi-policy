import logging
import random
import string
from datetime import timedelta

import requests
from django.conf import settings
from django.utils import timezone

from .models import DeviceFingerprint, GeDVerification, SMSOTPRequest

logger = logging.getLogger(__name__)

OTP_EXPIRY_MINUTES = 5
OTP_MAX_ATTEMPTS = 5


class SMSService:
    """Wrapper around smsoffice.ge API."""

    BASE_URL = "https://smsoffice.ge/api/v2"

    @staticmethod
    def generate_code() -> str:
        """Generate a 6-digit OTP code."""
        return "".join(random.choices(string.digits, k=6))

    def create_otp(self, phone_number: str) -> SMSOTPRequest:
        """Create an OTP record."""
        code = self.generate_code()
        expires_at = timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)

        return SMSOTPRequest.objects.create(
            phone_number=phone_number,
            code=code,
            expires_at=expires_at,
        )

    def send_sms(self, phone_number: str, message: str) -> dict | None:
        """Send SMS via smsoffice.ge API."""
        if not settings.SMS_API_KEY:
            logger.warning("SMS_API_KEY not configured, skipping SMS send")
            return None

        response = requests.post(
            f"{self.BASE_URL}/send/",
            json={
                "key": settings.SMS_API_KEY,
                "destination": phone_number,
                "sender": settings.SMS_SENDER,
                "content": message,
            },
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def send_otp(self, phone_number: str) -> SMSOTPRequest:
        """Generate OTP, persist it, send via SMS."""
        otp = self.create_otp(phone_number)
        message = f"Your Girchi verification code: {otp.code}"

        try:
            result = self.send_sms(phone_number, message)
            if result:
                otp.reference = str(result.get("MessageId", ""))
                otp.save(update_fields=["reference"])
        except requests.RequestException:
            logger.exception("Failed to send OTP SMS to %s", phone_number)

        return otp

    @staticmethod
    def verify_otp(phone_number: str, code: str) -> tuple[bool, str]:
        """Validate OTP code against stored record."""
        try:
            otp = SMSOTPRequest.objects.filter(
                phone_number=phone_number,
                is_verified=False,
            ).latest("created_at")
        except SMSOTPRequest.DoesNotExist:
            return False, "No OTP found for this phone number."

        if otp.is_expired:
            return False, "OTP has expired. Please request a new one."

        if otp.attempts >= OTP_MAX_ATTEMPTS:
            return False, "Too many attempts. Please request a new OTP."

        otp.attempts += 1

        if otp.code != code:
            otp.save(update_fields=["attempts"])
            remaining = OTP_MAX_ATTEMPTS - otp.attempts
            return False, f"Invalid code. {remaining} attempts remaining."

        otp.is_verified = True
        otp.save(update_fields=["attempts", "is_verified"])
        return True, "Phone number verified."


class GeDService:
    """Wrapper around girchi.com Strapi API for GeD verification."""

    def __init__(self):
        self.base_url = settings.GIRCHI_API_BASE_URL

    def verify_user(self, girchi_jwt: str) -> tuple[bool, dict]:
        """
        Call girchi.com API with user's JWT to verify GeD ownership.
        Returns (is_verified, data_dict) tuple.
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/users-permissions/users",
                headers={"Authorization": f"Bearer {girchi_jwt}"},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()

            if isinstance(data, list) and len(data) > 0:
                user_data = data[0]
            elif isinstance(data, dict):
                user_data = data
            else:
                return False, {}

            return True, user_data

        except requests.RequestException:
            logger.exception("Failed to verify GeD via girchi.com API")
            return False, {}

    def save_verification(self, user, girchi_jwt: str) -> GeDVerification | None:
        """Verify and persist GeD data for a user."""
        is_verified, data = self.verify_user(girchi_jwt)

        if not is_verified:
            return None

        verification, _ = GeDVerification.objects.update_or_create(
            user=user,
            defaults={
                "is_verified": True,
                "verified_at": timezone.now(),
                "girchi_user_id": data.get("id"),
                "ged_id": str(data.get("id", "")),
                "raw_response": data,
            },
        )

        user.role = "geder"
        user.save(update_fields=["role"])

        return verification


class DeviceFingerprintService:
    """Analyze device fingerprints for duplicate/suspicious patterns."""

    @staticmethod
    def check_and_save(
        user, fingerprint_hash: str, device_data: dict, ip_address: str | None = None
    ) -> tuple[DeviceFingerprint, bool]:
        """
        Store fingerprint and check for suspicious duplicates.
        Returns (fingerprint, is_suspicious) tuple.
        """
        is_suspicious = DeviceFingerprint.objects.filter(
            fingerprint_hash=fingerprint_hash,
        ).exclude(user=user).exists()

        fingerprint = DeviceFingerprint.objects.create(
            user=user,
            fingerprint_hash=fingerprint_hash,
            device_data=device_data,
            ip_address=ip_address,
            is_flagged=is_suspicious,
        )

        return fingerprint, is_suspicious
