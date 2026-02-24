from django.contrib import admin

from .models import ArbitrationCase


@admin.register(ArbitrationCase)
class ArbitrationCaseAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "case_type",
        "status",
        "tier",
        "complainant",
        "respondent",
        "arbitrator",
        "decided_at",
        "created_at",
    ]
    list_filter = ["case_type", "status", "tier", "created_at"]
    search_fields = [
        "title",
        "complainant__phone_number",
        "complainant__first_name",
        "complainant__last_name",
        "respondent__phone_number",
        "arbitrator__phone_number",
    ]
    readonly_fields = ["created_at", "updated_at", "decided_at"]
    raw_id_fields = ["complainant", "respondent", "arbitrator", "related_endorsement"]
    fieldsets = (
        ("Case Info", {"fields": ("case_type", "title", "description", "evidence")}),
        ("Status & Tier", {"fields": ("status", "tier")}),
        ("Parties", {"fields": ("complainant", "respondent", "arbitrator")}),
        ("Decision", {"fields": ("decision_text", "decided_at")}),
        ("Related", {"fields": ("related_endorsement",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
