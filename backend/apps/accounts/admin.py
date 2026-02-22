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
        "is_council_member",
        "created_at",
    ]
    list_filter = ["role", "member_status", "is_phone_verified", "onboarding_completed", "is_diaspora"]
    search_fields = ["phone_number", "personal_id_number", "first_name", "last_name"]
    ordering = ["-created_at"]
    readonly_fields = ["is_council_member"]

    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "personal_id_number")}),
        ("Role & Status", {"fields": ("role", "member_status", "is_diaspora", "is_council_member")}),
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

    def is_council_member(self, obj):
        """Display whether user is a council member."""
        return obj.is_council_member

    is_council_member.boolean = True
    is_council_member.short_description = "Council Member?"
