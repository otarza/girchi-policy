from rest_framework import serializers

from .models import GroupOfTen, Membership


class GroupOfTenSerializer(serializers.ModelSerializer):
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


class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = [
            "id",
            "user",
            "group",
            "is_active",
            "joined_at",
            "left_at",
        ]
        read_only_fields = ["joined_at"]
