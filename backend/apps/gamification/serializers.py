from rest_framework import serializers

from .models import TerritoryProgress, TierCapability


class TierCapabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = TierCapability
        fields = ["id", "tier", "key", "name", "description"]


class TerritoryProgressSerializer(serializers.ModelSerializer):
    precinct_id = serializers.IntegerField(source="precinct.id", read_only=True)
    precinct_name = serializers.CharField(source="precinct.name", read_only=True)
    precinct_cec_code = serializers.CharField(source="precinct.cec_code", read_only=True)
    unlocked_capabilities = serializers.SerializerMethodField()

    class Meta:
        model = TerritoryProgress
        fields = [
            "precinct_id",
            "precinct_name",
            "precinct_cec_code",
            "member_count",
            "group_count",
            "current_tier",
            "members_for_next_tier",
            "unlocked_capabilities",
            "updated_at",
        ]

    def get_unlocked_capabilities(self, obj):
        caps = TierCapability.objects.filter(tier__lte=obj.current_tier).order_by("tier", "key")
        return TierCapabilitySerializer(caps, many=True).data
