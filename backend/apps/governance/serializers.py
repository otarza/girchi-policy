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

    position = LeaderPositionMinimalSerializer(read_only=True)
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
        help_text="ID of the position being elected",
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
        Validate that election schedule makes sense:
        nomination_end <= voting_start <= voting_end
        """
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
