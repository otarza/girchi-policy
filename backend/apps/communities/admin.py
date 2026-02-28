from django.contrib import admin

from .models import Endorsement, EndorsementQuota, GroupOfTen, Membership


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


@admin.register(Endorsement)
class EndorsementAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "guarantor",
        "supporter",
        "status",
        "created_at",
        "revoked_at",
    ]
    list_filter = ["status", "created_at", "revoked_at"]
    search_fields = [
        "guarantor__phone_number",
        "guarantor__first_name",
        "guarantor__last_name",
        "supporter__phone_number",
        "supporter__first_name",
        "supporter__last_name",
    ]
    readonly_fields = ["created_at"]
    raw_id_fields = ["guarantor", "supporter"]
    date_hierarchy = "created_at"


@admin.register(EndorsementQuota)
class EndorsementQuotaAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "geder",
        "used_slots",
        "max_slots",
        "get_remaining_slots",
        "is_suspended",
        "suspended_at",
    ]
    list_filter = ["is_suspended", "suspended_at"]
    search_fields = [
        "geder__phone_number",
        "geder__first_name",
        "geder__last_name",
    ]
    readonly_fields = ["get_remaining_slots"]
    raw_id_fields = ["geder"]

    def get_remaining_slots(self, obj):
        return obj.remaining_slots

    get_remaining_slots.short_description = "Remaining"
