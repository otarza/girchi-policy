from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.territories.models import Precinct
from apps.territories.serializers import PrecinctSerializer
from .models import Endorsement, EndorsementQuota, GroupOfTen, Membership

User = get_user_model()


# ============================================================================
# MEMBERSHIP SERIALIZERS
# ============================================================================


class MembershipSerializer(serializers.ModelSerializer):
    """
    Serializer for Membership with user details.
    Used in group detail view to show member list.
    """

    user = serializers.SerializerMethodField()
    group_name = serializers.CharField(source="group.name", read_only=True)

    class Meta:
        model = Membership
        fields = [
            "id",
            "user",
            "group",
            "group_name",
            "is_active",
            "joined_at",
            "left_at",
        ]
        read_only_fields = ["joined_at", "left_at"]

    def get_user(self, obj):
        """Return user details for member list."""
        return {
            "id": obj.user.id,
            "phone_number": obj.user.phone_number,
            "full_name": obj.user.get_full_name(),
            "role": obj.user.role,
        }


# ============================================================================
# GROUP SERIALIZERS
# ============================================================================


class GroupOfTenListSerializer(serializers.ModelSerializer):
    """
    Optimized serializer for group list view.
    Does not include members array for performance.
    """

    precinct = PrecinctSerializer(read_only=True)
    member_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = GroupOfTen
        fields = [
            "id",
            "precinct",
            "name",
            "is_full",
            "member_count",
            "created_at",
        ]
        read_only_fields = ["is_full", "created_at"]


class GroupOfTenSerializer(serializers.ModelSerializer):
    """
    Full serializer for group detail view.
    Includes nested precinct and members list.
    """

    precinct = PrecinctSerializer(read_only=True)
    precinct_id = serializers.PrimaryKeyRelatedField(
        queryset=Precinct.objects.all(),
        source="precinct",
        write_only=True,
    )
    member_count = serializers.IntegerField(read_only=True)
    members = MembershipSerializer(many=True, read_only=True)

    class Meta:
        model = GroupOfTen
        fields = [
            "id",
            "precinct",
            "precinct_id",
            "name",
            "is_full",
            "member_count",
            "members",
            "created_at",
        ]
        read_only_fields = ["is_full", "created_at"]


# ============================================================================
# ENDORSEMENT SERIALIZERS
# ============================================================================


class EndorsementSerializer(serializers.ModelSerializer):
    """
    Serializer for Endorsement with user details.
    """

    guarantor = serializers.SerializerMethodField()
    supporter = serializers.SerializerMethodField()
    supporter_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="supporter",
        write_only=True,
    )

    class Meta:
        model = Endorsement
        fields = [
            "id",
            "guarantor",
            "supporter",
            "supporter_id",
            "status",
            "created_at",
            "revoked_at",
            "revoke_reason",
        ]
        read_only_fields = ["guarantor", "status", "created_at", "revoked_at"]

    def get_guarantor(self, obj):
        """Return guarantor user details."""
        return {
            "id": obj.guarantor.id,
            "phone_number": obj.guarantor.phone_number,
            "full_name": obj.guarantor.get_full_name(),
        }

    def get_supporter(self, obj):
        """Return supporter user details."""
        return {
            "id": obj.supporter.id,
            "phone_number": obj.supporter.phone_number,
            "full_name": obj.supporter.get_full_name(),
            "role": obj.supporter.role,
        }


class EndorsementQuotaSerializer(serializers.ModelSerializer):
    """
    Serializer for EndorsementQuota.
    """

    remaining_slots = serializers.IntegerField(read_only=True)

    class Meta:
        model = EndorsementQuota
        fields = [
            "max_slots",
            "used_slots",
            "remaining_slots",
            "is_suspended",
            "suspended_at",
            "suspended_reason",
        ]
        read_only_fields = ["used_slots", "suspended_at"]
