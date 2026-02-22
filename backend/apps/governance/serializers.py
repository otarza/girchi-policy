from django.contrib.auth import get_user_model
from django.db.models import Count
from rest_framework import serializers

from .models import Candidacy, Election, LeaderPosition, Vote

User = get_user_model()


# ============================================================================
# LEADER POSITION SERIALIZER (Minimal for nesting)
# ============================================================================


class LeaderPositionMinimalSerializer(serializers.ModelSerializer):
    """
    Minimal serializer for LeaderPosition.
    Used for nested display in election detail.
    """

    tier_name = serializers.CharField(source="get_tier_display", read_only=True)
    territory_name = serializers.SerializerMethodField()
    holder = serializers.SerializerMethodField()

    class Meta:
        model = LeaderPosition
        fields = ["id", "tier", "tier_name", "territory_name", "holder"]
        read_only_fields = fields

    def get_territory_name(self, obj):
        """Return territory name."""
        return obj.territory_name

    def get_holder(self, obj):
        """Return holder details if present."""
        if obj.holder:
            return {
                "id": obj.holder.id,
                "phone_number": obj.holder.phone_number,
                "full_name": obj.holder.get_full_name(),
            }
        return None


class LeaderPositionListSerializer(serializers.ModelSerializer):
    """
    Optimized serializer for position list view.
    Includes holder details and territory name for display.
    """

    tier_name = serializers.CharField(read_only=True)
    territory_name = serializers.CharField(read_only=True)
    is_vacant = serializers.BooleanField(read_only=True)
    holder = serializers.SerializerMethodField()

    class Meta:
        model = LeaderPosition
        fields = [
            "id",
            "tier",
            "tier_name",
            "territory_name",
            "holder",
            "held_since",
            "is_vacant",
            "is_active",
            "created_at",
        ]
        read_only_fields = fields

    def get_holder(self, obj):
        """Return holder user details if position is held."""
        if not obj.holder:
            return None
        return {
            "id": obj.holder.id,
            "phone_number": obj.holder.phone_number,
            "full_name": obj.holder.get_full_name(),
            "role": obj.holder.role,
        }


class LeaderPositionDetailSerializer(serializers.ModelSerializer):
    """
    Full serializer for position detail view.
    Includes nested territory data, parent/children relationships.
    """

    tier_name = serializers.CharField(read_only=True)
    territory_name = serializers.CharField(read_only=True)
    is_vacant = serializers.BooleanField(read_only=True)
    holder = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()
    precinct = serializers.SerializerMethodField()
    district = serializers.SerializerMethodField()
    parent = LeaderPositionMinimalSerializer(read_only=True)

    class Meta:
        model = LeaderPosition
        fields = [
            "id",
            "tier",
            "tier_name",
            "territory_name",
            "group",
            "precinct",
            "district",
            "holder",
            "held_since",
            "is_vacant",
            "is_active",
            "parent",
            "created_at",
        ]
        read_only_fields = fields

    def get_holder(self, obj):
        """Return detailed holder information."""
        if not obj.holder:
            return None
        return {
            "id": obj.holder.id,
            "phone_number": obj.holder.phone_number,
            "full_name": obj.holder.get_full_name(),
            "role": obj.holder.role,
            "member_status": obj.holder.member_status,
        }

    def get_group(self, obj):
        """Return group details if tier=10."""
        if not obj.group:
            return None
        return {
            "id": obj.group.id,
            "name": obj.group.name,
        }

    def get_precinct(self, obj):
        """Return precinct details if set."""
        if not obj.precinct:
            return None
        return {
            "id": obj.precinct.id,
            "name": obj.precinct.name,
            "name_ka": obj.precinct.name_ka,
        }

    def get_district(self, obj):
        """Return district details if set."""
        if not obj.district:
            return None
        return {
            "id": obj.district.id,
            "name": obj.district.name,
            "name_ka": obj.district.name_ka,
        }


class HierarchyNodeSerializer(serializers.Serializer):
    """
    Serializer for a single position in the hierarchy tree.
    Includes nested children for recursive tree structure.
    """

    id = serializers.IntegerField()
    tier = serializers.IntegerField()
    tier_name = serializers.CharField()
    territory_name = serializers.CharField()
    holder = serializers.SerializerMethodField()
    is_vacant = serializers.BooleanField()
    children = serializers.SerializerMethodField()

    def get_holder(self, obj):
        """Return holder details."""
        if not obj.holder:
            return None
        return {
            "id": obj.holder.id,
            "phone_number": obj.holder.phone_number,
            "full_name": obj.holder.get_full_name(),
            "role": obj.holder.role,
        }

    def get_children(self, obj):
        """
        Return children positions at the tier below.
        Recursively serializes child positions.
        """
        # Get context to check if we should include children
        include_children = self.context.get("include_children", True)
        max_depth = self.context.get("max_depth", 4)  # Default: all 4 tiers
        current_depth = self.context.get("current_depth", 0)

        if not include_children or current_depth >= max_depth:
            return []

        # Get child positions using the helper method
        child_positions = obj.get_child_positions()

        if not child_positions.exists():
            return []

        # Increment depth for recursion
        child_context = self.context.copy()
        child_context["current_depth"] = current_depth + 1

        # Serialize children recursively
        return HierarchyNodeSerializer(
            child_positions, many=True, context=child_context
        ).data


# ============================================================================
# CANDIDACY SERIALIZERS
# ============================================================================


class CandidacySerializer(serializers.ModelSerializer):
    """
    Serializer for Candidacy with candidate details.
    """

    candidate = serializers.SerializerMethodField()
    vote_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Candidacy
        fields = [
            "id",
            "election",
            "candidate",
            "statement",
            "registered_at",
            "is_approved",
            "vote_count",
        ]
        read_only_fields = ["election", "registered_at", "is_approved", "vote_count"]

    def get_candidate(self, obj):
        """Return candidate user details."""
        return {
            "id": obj.candidate.id,
            "phone_number": obj.candidate.phone_number,
            "full_name": obj.candidate.get_full_name(),
            "role": obj.candidate.role,
            "member_status": obj.candidate.member_status,
        }


# ============================================================================
# VOTE SERIALIZERS
# ============================================================================


class VoteSerializer(serializers.ModelSerializer):
    """
    Serializer for Vote with voter details.
    """

    voter = serializers.SerializerMethodField()
    candidacy_id = serializers.PrimaryKeyRelatedField(
        queryset=Candidacy.objects.all(), source="candidacy", write_only=True
    )

    class Meta:
        model = Vote
        fields = ["id", "election", "voter", "candidacy", "candidacy_id", "cast_at"]
        read_only_fields = ["election", "voter", "candidacy", "cast_at"]

    def get_voter(self, obj):
        """Return voter user details."""
        return {
            "id": obj.voter.id,
            "phone_number": obj.voter.phone_number,
            "full_name": obj.voter.get_full_name(),
        }


# ============================================================================
# ELECTION SERIALIZERS
# ============================================================================


class ElectionListSerializer(serializers.ModelSerializer):
    """
    Optimized serializer for election list view.
    Does not include candidacies array for performance.
    """

    position = LeaderPositionMinimalSerializer(read_only=True)
    candidate_count = serializers.IntegerField(read_only=True)
    vote_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Election
        fields = [
            "id",
            "election_type",
            "status",
            "position",
            "nomination_start",
            "nomination_end",
            "voting_start",
            "voting_end",
            "candidate_count",
            "vote_count",
            "created_at",
        ]
        read_only_fields = fields


class ElectionDetailSerializer(serializers.ModelSerializer):
    """
    Full serializer for election detail view.
    Includes nested position and candidacies.
    """

    position = LeaderPositionMinimalSerializer(read_only=True, allow_null=True)
    candidacies = CandidacySerializer(many=True, read_only=True)
    total_votes = serializers.IntegerField(read_only=True)

    class Meta:
        model = Election
        fields = [
            "id",
            "election_type",
            "status",
            "position",
            "nomination_start",
            "nomination_end",
            "voting_start",
            "voting_end",
            "candidacies",
            "total_votes",
            "created_by",
            "created_at",
        ]
        read_only_fields = fields


class ElectionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating elections.
    """

    position_id = serializers.PrimaryKeyRelatedField(
        queryset=LeaderPosition.objects.all(),
        source="position",
        write_only=True,
        required=False,
        allow_null=True,
        help_text="ID of the position being elected (null for parliamentary elections)",
    )

    class Meta:
        model = Election
        fields = [
            "election_type",
            "position_id",
            "nomination_start",
            "nomination_end",
            "voting_start",
            "voting_end",
        ]

    def validate(self, data):
        """
        Validate election creation based on election type and schedule.

        Rules:
        - Parliamentary elections: position must be None
        - Hierarchy/Atistavi elections: position is required
        - Schedule: nomination_end <= voting_start <= voting_end
        """
        from .models import ElectionType

        election_type = data.get("election_type")
        position = data.get("position")

        # Validate position based on election type
        if election_type == ElectionType.PARLIAMENTARY:
            if position is not None:
                raise serializers.ValidationError(
                    {"position_id": "Parliamentary elections cannot have a position."}
                )
        else:
            # Hierarchy or atistavi elections require a position
            if position is None:
                raise serializers.ValidationError(
                    {
                        "position_id": "Position is required for atistavi and hierarchy elections."
                    }
                )

        # Validate schedule
        nomination_end = data.get("nomination_end")
        voting_start = data.get("voting_start")
        voting_end = data.get("voting_end")

        if nomination_end > voting_start:
            raise serializers.ValidationError(
                {"nomination_end": "Nomination period must end before voting starts."}
            )

        if voting_start > voting_end:
            raise serializers.ValidationError(
                {"voting_end": "Voting period end must be after voting start."}
            )

        return data


class ElectionResultsSerializer(serializers.Serializer):
    """
    Serializer for election results endpoint.
    Returns vote tallies and winner.
    """

    election_id = serializers.IntegerField()
    status = serializers.CharField()
    winner = serializers.SerializerMethodField()
    results = serializers.SerializerMethodField()
    total_votes = serializers.IntegerField()
    total_eligible_voters = serializers.IntegerField()

    def get_winner(self, obj):
        """Return the winning candidacy with vote count."""
        winner = obj.get("winner")
        if winner:
            return {
                "candidacy_id": winner.id,
                "candidate_name": winner.candidate.get_full_name()
                or winner.candidate.phone_number,
                "candidate_id": winner.candidate.id,
                "votes": winner.vote_count,
                "statement": winner.statement,
            }
        return None

    def get_results(self, obj):
        """Return array of all candidacies with vote counts."""
        results = obj.get("results", [])
        return [
            {
                "candidacy_id": candidacy.id,
                "candidate_name": candidacy.candidate.get_full_name()
                or candidacy.candidate.phone_number,
                "candidate_id": candidacy.candidate.id,
                "votes": candidacy.vote_count,
            }
            for candidacy in results
        ]
