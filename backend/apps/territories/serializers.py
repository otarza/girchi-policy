from rest_framework import serializers

from .models import District, Precinct, Region


class RegionSerializer(serializers.ModelSerializer):
    """Serializer for Region model."""

    class Meta:
        model = Region
        fields = ["id", "name", "name_ka", "code"]


class DistrictSerializer(serializers.ModelSerializer):
    """Serializer for District model with nested region."""

    region = RegionSerializer(read_only=True)

    class Meta:
        model = District
        fields = ["id", "region", "name", "name_ka", "cec_code"]


class PrecinctSerializer(serializers.ModelSerializer):
    """Serializer for Precinct model with nested district and region."""

    district = DistrictSerializer(read_only=True)

    class Meta:
        model = Precinct
        fields = [
            "id",
            "district",
            "name",
            "name_ka",
            "cec_code",
            "latitude",
            "longitude",
        ]


class PrecinctWithDistanceSerializer(PrecinctSerializer):
    """Extends PrecinctSerializer with distance field for nearby searches."""

    distance = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta(PrecinctSerializer.Meta):
        fields = PrecinctSerializer.Meta.fields + ["distance"]
