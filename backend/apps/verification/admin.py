from django.contrib import admin

from .models import DeviceFingerprint, GeDVerification, SMSOTPRequest


@admin.register(SMSOTPRequest)
class SMSOTPRequestAdmin(admin.ModelAdmin):
    list_display = ["phone_number", "is_verified", "attempts", "created_at", "expires_at"]
    list_filter = ["is_verified"]
    search_fields = ["phone_number"]
    readonly_fields = ["code", "reference", "created_at"]


@admin.register(GeDVerification)
class GeDVerificationAdmin(admin.ModelAdmin):
    list_display = ["user", "ged_id", "is_verified", "ged_balance", "verified_at", "last_sync_at"]
    list_filter = ["is_verified"]
    search_fields = ["user__phone_number", "ged_id"]
    raw_id_fields = ["user"]


@admin.register(DeviceFingerprint)
class DeviceFingerprintAdmin(admin.ModelAdmin):
    list_display = ["user", "fingerprint_hash", "ip_address", "is_flagged", "created_at"]
    list_filter = ["is_flagged"]
    search_fields = ["user__phone_number", "fingerprint_hash"]
    raw_id_fields = ["user"]
