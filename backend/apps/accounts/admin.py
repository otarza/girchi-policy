from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        "phone_number",
        "first_name",
        "last_name",
        "role",
        "member_status",
        "is_phone_verified",
        "onboarding_completed",
        "is_diaspora",
        "created_at",
    ]
    list_filter = ["role", "member_status", "is_phone_verified", "onboarding_completed", "is_diaspora"]
    search_fields = ["phone_number", "personal_id_number", "first_name", "last_name"]
    ordering = ["-created_at"]

    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "personal_id_number")}),
        ("Role & Status", {"fields": ("role", "member_status", "is_diaspora")}),
        (
            "Onboarding",
            {
                "fields": (
                    "is_phone_verified",
                    "onboarding_completed",
                    "join_reason",
                    "constitution_accepted",
                    "constitution_accepted_at",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Dates", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("phone_number", "password1", "password2"),
            },
        ),
    )
