from django.contrib import admin

from .models import Candidacy, Election, LeaderPosition, Vote


@admin.register(LeaderPosition)
class LeaderPositionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "tier",
        "tier_name",
        "territory_name",
        "holder",
        "held_since",
        "is_active",
        "created_at",
    ]
    list_filter = ["tier", "is_active", "held_since", "created_at"]
    search_fields = [
        "holder__phone_number",
        "holder__first_name",
        "holder__last_name",
        "group__name",
        "precinct__name",
        "precinct__name_ka",
        "district__name",
        "district__name_ka",
    ]
    readonly_fields = ["created_at", "tier_name", "territory_name", "is_vacant"]
    raw_id_fields = ["holder", "group", "precinct", "district", "parent"]
    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Position Info",
            {
                "fields": ("tier", "tier_name", "is_active"),
            },
        ),
        (
            "Territory Assignment",
            {
                "fields": ("group", "precinct", "district", "territory_name"),
                "description": "Only one of group/precinct/district should be set based on tier",
            },
        ),
        (
            "Holder Info",
            {
                "fields": ("holder", "held_since", "is_vacant"),
            },
        ),
        (
            "Hierarchy",
            {
                "fields": ("parent",),
            },
        ),
        (
            "Metadata",
            {
                "fields": ("created_at",),
            },
        ),
    )

    def tier_name(self, obj):
        """Display human-readable tier name."""
        return obj.tier_name

    tier_name.short_description = "Tier Name"

    def territory_name(self, obj):
        """Display territory name."""
        return obj.territory_name

    territory_name.short_description = "Territory"

    def is_vacant(self, obj):
        """Display vacancy status."""
        return obj.is_vacant

    is_vacant.boolean = True
    is_vacant.short_description = "Vacant?"


@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "election_type",
        "status",
        "position",
        "nomination_start",
        "voting_start",
        "voting_end",
        "created_at",
    ]
    list_filter = ["election_type", "status", "created_at"]
    search_fields = [
        "position__group__name",
        "position__precinct__name",
        "position__precinct__name_ka",
        "created_by__phone_number",
        "created_by__first_name",
        "created_by__last_name",
    ]
    readonly_fields = [
        "created_at",
        "is_nomination_period",
        "is_voting_period",
        "is_finished",
    ]
    raw_id_fields = ["position", "created_by"]
    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Election Info",
            {
                "fields": ("election_type", "status", "position"),
            },
        ),
        (
            "Schedule",
            {
                "fields": (
                    "nomination_start",
                    "nomination_end",
                    "voting_start",
                    "voting_end",
                    "is_nomination_period",
                    "is_voting_period",
                ),
            },
        ),
        (
            "Status",
            {
                "fields": ("is_finished",),
            },
        ),
        (
            "Metadata",
            {
                "fields": ("created_by", "created_at"),
            },
        ),
    )

    def is_nomination_period(self, obj):
        """Display whether election is in nomination period."""
        return obj.is_nomination_period

    is_nomination_period.boolean = True
    is_nomination_period.short_description = "Nomination Open?"

    def is_voting_period(self, obj):
        """Display whether election is in voting period."""
        return obj.is_voting_period

    is_voting_period.boolean = True
    is_voting_period.short_description = "Voting Open?"

    def is_finished(self, obj):
        """Display whether election is finished."""
        return obj.is_finished

    is_finished.boolean = True
    is_finished.short_description = "Finished?"


@admin.register(Candidacy)
class CandidacyAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "election",
        "candidate",
        "is_approved",
        "registered_at",
        "vote_count",
    ]
    list_filter = ["is_approved", "registered_at"]
    search_fields = [
        "candidate__phone_number",
        "candidate__first_name",
        "candidate__last_name",
        "election__id",
    ]
    readonly_fields = ["registered_at", "vote_count"]
    raw_id_fields = ["election", "candidate"]
    date_hierarchy = "registered_at"

    def vote_count(self, obj):
        """Display vote count for this candidacy."""
        return obj.vote_count

    vote_count.short_description = "Votes"


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ["id", "election", "voter", "candidacy", "cast_at"]
    list_filter = ["cast_at", "election__election_type"]
    search_fields = [
        "voter__phone_number",
        "voter__first_name",
        "voter__last_name",
        "candidacy__candidate__phone_number",
        "candidacy__candidate__first_name",
        "candidacy__candidate__last_name",
    ]
    readonly_fields = ["cast_at"]
    raw_id_fields = ["election", "voter", "candidacy"]
    date_hierarchy = "cast_at"
