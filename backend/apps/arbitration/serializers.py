from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.communities.models import Endorsement

from .models import ArbitrationCase

User = get_user_model()


class ArbitrationCaseCreateSerializer(serializers.ModelSerializer):
    """Serializer for filing a new arbitration case."""

    respondent_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="respondent",
        required=False,
        allow_null=True,
    )
    related_endorsement_id = serializers.PrimaryKeyRelatedField(
        queryset=Endorsement.objects.all(),
        source="related_endorsement",
        required=False,
        allow_null=True,
    )

    class Meta:
        model = ArbitrationCase
        fields = [
            "case_type",
            "title",
            "description",
            "evidence",
            "respondent_id",
            "related_endorsement_id",
        ]

    def validate(self, data):
        case_type = data.get("case_type")
        if case_type == ArbitrationCase.CaseType.ENDORSEMENT_FRAUD:
            if not data.get("related_endorsement"):
                raise serializers.ValidationError(
                    {"related_endorsement_id": "Endorsement fraud cases require a related_endorsement_id."}
                )
        return data


class ArbitrationCaseListSerializer(serializers.ModelSerializer):
    """Optimized list serializer."""

    case_type_display = serializers.CharField(source="get_case_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    complainant = serializers.SerializerMethodField()
    respondent = serializers.SerializerMethodField()

    class Meta:
        model = ArbitrationCase
        fields = [
            "id",
            "case_type",
            "case_type_display",
            "status",
            "status_display",
            "title",
            "tier",
            "complainant",
            "respondent",
            "decided_at",
            "created_at",
        ]
        read_only_fields = fields

    def get_complainant(self, obj):
        return {
            "id": obj.complainant.id,
            "phone_number": obj.complainant.phone_number,
            "full_name": obj.complainant.get_full_name() or obj.complainant.phone_number,
        }

    def get_respondent(self, obj):
        if not obj.respondent:
            return None
        return {
            "id": obj.respondent.id,
            "phone_number": obj.respondent.phone_number,
            "full_name": obj.respondent.get_full_name() or obj.respondent.phone_number,
        }


class ArbitrationCaseDetailSerializer(serializers.ModelSerializer):
    """Full detail serializer."""

    case_type_display = serializers.CharField(source="get_case_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    complainant = serializers.SerializerMethodField()
    respondent = serializers.SerializerMethodField()
    arbitrator = serializers.SerializerMethodField()
    can_appeal = serializers.BooleanField(read_only=True)
    next_appeal_tier = serializers.IntegerField(read_only=True, allow_null=True)

    class Meta:
        model = ArbitrationCase
        fields = [
            "id",
            "case_type",
            "case_type_display",
            "status",
            "status_display",
            "title",
            "description",
            "evidence",
            "tier",
            "complainant",
            "respondent",
            "arbitrator",
            "decision_text",
            "decided_at",
            "can_appeal",
            "next_appeal_tier",
            "related_endorsement",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_complainant(self, obj):
        return {
            "id": obj.complainant.id,
            "phone_number": obj.complainant.phone_number,
            "full_name": obj.complainant.get_full_name() or obj.complainant.phone_number,
        }

    def get_respondent(self, obj):
        if not obj.respondent:
            return None
        return {
            "id": obj.respondent.id,
            "phone_number": obj.respondent.phone_number,
            "full_name": obj.respondent.get_full_name() or obj.respondent.phone_number,
        }

    def get_arbitrator(self, obj):
        if not obj.arbitrator:
            return None
        return {
            "id": obj.arbitrator.id,
            "phone_number": obj.arbitrator.phone_number,
            "full_name": obj.arbitrator.get_full_name() or obj.arbitrator.phone_number,
        }
