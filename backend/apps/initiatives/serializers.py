from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.territories.models import District, Precinct

from .models import Initiative, InitiativeSignature

User = get_user_model()


class InitiativeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating initiatives."""

    precinct_id = serializers.PrimaryKeyRelatedField(
        queryset=Precinct.objects.all(),
        source="precinct",
        required=False,
        allow_null=True,
    )
    district_id = serializers.PrimaryKeyRelatedField(
        queryset=District.objects.all(),
        source="district",
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Initiative
        fields = ["title", "description", "precinct_id", "district_id", "signature_threshold"]

    def validate_signature_threshold(self, value):
        if value < 10:
            raise serializers.ValidationError("Signature threshold must be at least 10.")
        return value

    def validate(self, data):
        if not data.get("precinct") and not data.get("district"):
            raise serializers.ValidationError(
                "At least one of precinct_id or district_id must be provided."
            )
        return data


class InitiativeListSerializer(serializers.ModelSerializer):
    """Optimized serializer for list view with signature count."""

    status_display = serializers.CharField(source="get_status_display", read_only=True)
    author = serializers.SerializerMethodField()
    signature_count = serializers.IntegerField(read_only=True)
    territory = serializers.SerializerMethodField()

    class Meta:
        model = Initiative
        fields = [
            "id",
            "title",
            "status",
            "status_display",
            "signature_threshold",
            "signature_count",
            "author",
            "territory",
            "created_at",
        ]
        read_only_fields = fields

    def get_author(self, obj):
        return {
            "id": obj.author.id,
            "phone_number": obj.author.phone_number,
            "full_name": obj.author.get_full_name() or obj.author.phone_number,
        }

    def get_territory(self, obj):
        if obj.precinct:
            return {"type": "precinct", "id": obj.precinct.id, "name": obj.precinct.name}
        if obj.district:
            return {"type": "district", "id": obj.district.id, "name": obj.district.name}
        return None


class InitiativeDetailSerializer(serializers.ModelSerializer):
    """Full detail serializer with signature count and response."""

    status_display = serializers.CharField(source="get_status_display", read_only=True)
    author = serializers.SerializerMethodField()
    signature_count = serializers.IntegerField(read_only=True)
    territory = serializers.SerializerMethodField()
    responded_by = serializers.SerializerMethodField()

    class Meta:
        model = Initiative
        fields = [
            "id",
            "title",
            "description",
            "status",
            "status_display",
            "signature_threshold",
            "signature_count",
            "author",
            "territory",
            "response_text",
            "responded_by",
            "responded_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_author(self, obj):
        return {
            "id": obj.author.id,
            "phone_number": obj.author.phone_number,
            "full_name": obj.author.get_full_name() or obj.author.phone_number,
        }

    def get_territory(self, obj):
        if obj.precinct:
            return {"type": "precinct", "id": obj.precinct.id, "name": obj.precinct.name}
        if obj.district:
            return {"type": "district", "id": obj.district.id, "name": obj.district.name}
        return None

    def get_responded_by(self, obj):
        if not obj.responded_by:
            return None
        return {
            "id": obj.responded_by.id,
            "phone_number": obj.responded_by.phone_number,
            "full_name": obj.responded_by.get_full_name() or obj.responded_by.phone_number,
        }
