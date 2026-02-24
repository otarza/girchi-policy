from django.contrib import admin

from .models import SOSEscalation, SOSReport


class SOSEscalationInline(admin.TabularInline):
    model = SOSEscalation
    extra = 0
    readonly_fields = ["from_level", "to_level", "escalated_by", "note", "created_at"]
    can_delete = False


@admin.register(SOSReport)
class SOSReportAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "reporter",
        "status",
        "escalation_level",
        "assigned_to",
        "created_at",
    ]
    list_filter = ["status", "escalation_level", "created_at"]
    search_fields = [
        "title",
        "reporter__phone_number",
        "reporter__first_name",
        "reporter__last_name",
        "assigned_to__phone_number",
    ]
    readonly_fields = ["created_at", "updated_at", "resolved_at"]
    raw_id_fields = ["reporter", "assigned_to"]
    inlines = [SOSEscalationInline]
    fieldsets = (
        ("Report Info", {"fields": ("title", "description", "moral_filter_answer")}),
        ("Status", {"fields": ("status", "escalation_level", "assigned_to")}),
        ("Reporter", {"fields": ("reporter",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at", "resolved_at")}),
    )


@admin.register(SOSEscalation)
class SOSEscalationAdmin(admin.ModelAdmin):
    list_display = ["id", "report", "from_level", "to_level", "escalated_by", "created_at"]
    list_filter = ["from_level", "to_level", "created_at"]
    search_fields = ["report__title", "escalated_by__phone_number"]
    readonly_fields = ["created_at"]
    raw_id_fields = ["report", "escalated_by"]
