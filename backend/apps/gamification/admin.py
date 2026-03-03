from django.contrib import admin

from .models import TerritoryProgress, TierCapability


@admin.register(TerritoryProgress)
class TerritoryProgressAdmin(admin.ModelAdmin):
    list_display = ("precinct", "member_count", "group_count", "current_tier", "members_for_next_tier", "updated_at")
    list_filter = ("current_tier",)
    search_fields = ("precinct__name", "precinct__cec_code")
    readonly_fields = ("updated_at",)
    ordering = ("-member_count",)


@admin.register(TierCapability)
class TierCapabilityAdmin(admin.ModelAdmin):
    list_display = ("tier", "key", "name", "description")
    list_filter = ("tier",)
    search_fields = ("key", "name")
    ordering = ("tier", "key")
