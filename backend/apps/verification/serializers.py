from rest_framework import serializers

from .models import GeDVerification


class SendOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=6, min_length=6)


class GeDVerifySerializer(serializers.Serializer):
    girchi_jwt = serializers.CharField()


class GeDVerificationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeDVerification
        fields = [
            "is_verified",
            "ged_id",
            "ged_balance",
            "verified_at",
            "last_sync_at",
        ]


class DeviceFingerprintSerializer(serializers.Serializer):
    fingerprint_hash = serializers.CharField(max_length=255)
    device_data = serializers.JSONField(required=False, default=dict)
