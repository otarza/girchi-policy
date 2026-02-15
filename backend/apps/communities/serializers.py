from rest_framework import serializers

from apps.territories.models import Precinct
from apps.territories.serializers import PrecinctSerializer
from .models import GroupOfTen, Membership


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
