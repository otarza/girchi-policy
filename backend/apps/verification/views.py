from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.throttling import OTPRateThrottle

from .serializers import (
    DeviceFingerprintSerializer,
    GeDVerificationStatusSerializer,
    GeDVerifySerializer,
    SendOTPSerializer,
    VerifyOTPSerializer,
)
from .services import DeviceFingerprintService, GeDService, SMSService

User = get_user_model()


class SendOTPView(APIView):
    """Send OTP to a phone number."""

    permission_classes = [AllowAny]
    throttle_classes = [OTPRateThrottle]

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        sms_service = SMSService()
        otp = sms_service.send_otp(serializer.validated_data["phone_number"])

        return Response(
            {"detail": "OTP sent.", "expires_at": otp.expires_at},
            status=status.HTTP_200_OK,
        )


class VerifyOTPView(APIView):
    """Verify an OTP code."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone_number"]
        code = serializer.validated_data["code"]

        success, message = SMSService.verify_otp(phone, code)

        if success:
            User.objects.filter(phone_number=phone).update(is_phone_verified=True)
            return Response(
                {"verified": True, "message": message},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"verified": False, "message": message},
            status=status.HTTP_400_BAD_REQUEST,
        )


class GeDVerifyView(APIView):
    """Initiate GeD verification via girchi.com API."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = GeDVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ged_service = GeDService()
        verification = ged_service.save_verification(
            request.user, serializer.validated_data["girchi_jwt"]
        )

        if verification is None:
            return Response(
                {"detail": "GeD verification failed. Please check your credentials."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            GeDVerificationStatusSerializer(verification).data,
            status=status.HTTP_200_OK,
        )


class GeDStatusView(APIView):
    """Check current GeD verification status."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            verification = request.user.ged_verification
        except Exception:
            return Response(
                {"is_verified": False, "detail": "No GeD verification on record."},
                status=status.HTTP_200_OK,
            )

        return Response(
            GeDVerificationStatusSerializer(verification).data,
            status=status.HTTP_200_OK,
        )


class DeviceFingerprintView(APIView):
    """Submit device fingerprint for anti-fake detection."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DeviceFingerprintSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ip_address = request.META.get("REMOTE_ADDR")

        fingerprint, is_suspicious = DeviceFingerprintService.check_and_save(
            user=request.user,
            fingerprint_hash=serializer.validated_data["fingerprint_hash"],
            device_data=serializer.validated_data.get("device_data", {}),
            ip_address=ip_address,
        )

        return Response(
            {"recorded": True, "is_flagged": fingerprint.is_flagged},
            status=status.HTTP_201_CREATED,
        )
