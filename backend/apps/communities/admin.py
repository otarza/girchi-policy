from django.contrib import admin

from .models import GroupOfTen, Membership


@admin.register(GroupOfTen)
class GroupOfTenAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "precinct",
        "get_member_count",
        "is_full",
        "created_at",
    ]
    list_filter = ["is_full", "precinct__district__region", "created_at"]
    search_fields = ["name", "precinct__name", "precinct__name_ka"]
    readonly_fields = ["created_at"]
    raw_id_fields = ["precinct"]

    def get_member_count(self, obj):
        return obj.member_count

    get_member_count.short_description = "Members"


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "group",
        "is_active",
        "joined_at",
        "left_at",
    ]
    list_filter = ["is_active", "joined_at", "left_at"]
    search_fields = [
        "user__phone_number",
        "user__first_name",
        "user__last_name",
        "group__name",
    ]
    readonly_fields = ["joined_at"]
    raw_id_fields = ["user", "group"]
    date_hierarchy = "joined_at"
