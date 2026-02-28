from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import EscalationLevel, SOSEscalation, SOSReport

User = get_user_model()


class UserMinimalSerializer(serializers.Serializer):
    """Minimal user representation for nested display."""

    id = serializers.IntegerField()
    phone_number = serializers.CharField()
    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.phone_number


class SOSEscalationSerializer(serializers.ModelSerializer):
    """Serializer for escalation audit records."""

    from_level_display = serializers.CharField(
        source="get_from_level_display", read_only=True
    )
    to_level_display = serializers.CharField(
        source="get_to_level_display", read_only=True
    )
    escalated_by = serializers.SerializerMethodField()

    class Meta:
        model = SOSEscalation
        fields = [
            "id",
            "from_level",
            "from_level_display",
            "to_level",
            "to_level_display",
            "escalated_by",
            "note",
            "created_at",
        ]
        read_only_fields = fields

    def get_escalated_by(self, obj):
        if obj.escalated_by:
            return {
                "id": obj.escalated_by.id,
                "phone_number": obj.escalated_by.phone_number,
                "full_name": obj.escalated_by.get_full_name() or obj.escalated_by.phone_number,
            }
        return None  # Auto-escalated by system


class SOSReportCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating SOS reports."""

    class Meta:
        model = SOSReport
        fields = ["title", "description", "moral_filter_answer"]

    def validate_moral_filter_answer(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Moral filter answer must be at least 10 characters."
            )
        return value


class SOSReportListSerializer(serializers.ModelSerializer):
    """Optimized serializer for list view."""

    status_display = serializers.CharField(source="get_status_display", read_only=True)
    escalation_level_display = serializers.CharField(
        source="get_escalation_level_display", read_only=True
    )
    reporter = serializers.SerializerMethodField()
    assigned_to = serializers.SerializerMethodField()

    class Meta:
        model = SOSReport
        fields = [
            "id",
            "title",
            "status",
            "status_display",
            "escalation_level",
            "escalation_level_display",
            "reporter",
            "assigned_to",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_reporter(self, obj):
        return {
            "id": obj.reporter.id,
            "phone_number": obj.reporter.phone_number,
            "full_name": obj.reporter.get_full_name() or obj.reporter.phone_number,
        }

    def get_assigned_to(self, obj):
        if not obj.assigned_to:
            return None
        return {
            "id": obj.assigned_to.id,
            "phone_number": obj.assigned_to.phone_number,
            "full_name": obj.assigned_to.get_full_name() or obj.assigned_to.phone_number,
        }


class SOSReportDetailSerializer(serializers.ModelSerializer):
    """Full serializer for detail view including escalation history."""

    status_display = serializers.CharField(source="get_status_display", read_only=True)
    escalation_level_display = serializers.CharField(
        source="get_escalation_level_display", read_only=True
    )
    reporter = serializers.SerializerMethodField()
    assigned_to = serializers.SerializerMethodField()
    escalations = SOSEscalationSerializer(many=True, read_only=True)
    next_escalation_level = serializers.SerializerMethodField()

    class Meta:
        model = SOSReport
        fields = [
            "id",
            "title",
            "description",
            "moral_filter_answer",
            "status",
            "status_display",
            "escalation_level",
            "escalation_level_display",
            "next_escalation_level",
            "reporter",
            "assigned_to",
            "escalations",
            "resolved_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_reporter(self, obj):
        return {
            "id": obj.reporter.id,
            "phone_number": obj.reporter.phone_number,
            "full_name": obj.reporter.get_full_name() or obj.reporter.phone_number,
        }

    def get_assigned_to(self, obj):
        if not obj.assigned_to:
            return None
        return {
            "id": obj.assigned_to.id,
            "phone_number": obj.assigned_to.phone_number,
            "full_name": obj.assigned_to.get_full_name() or obj.assigned_to.phone_number,
        }

    def get_next_escalation_level(self, obj):
        next_level = obj.get_next_escalation_level()
        if next_level is None:
            return None
        return {
            "value": next_level,
            "display": EscalationLevel(next_level).label,
        }
