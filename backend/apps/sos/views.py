from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.permissions import IsAtistavi, IsLeaderAtTier, IsVerifiedMember

from .models import EscalationLevel, SOSEscalation, SOSReport
from .serializers import (
    SOSReportCreateSerializer,
    SOSReportDetailSerializer,
    SOSReportListSerializer,
)


class SOSReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for SOS Report CRUD and lifecycle actions.

    Actions:
    - list:     GET  /api/v1/sos/reports/
    - retrieve: GET  /api/v1/sos/reports/{id}/
    - create:   POST /api/v1/sos/reports/
    - verify:   POST /api/v1/sos/reports/{id}/verify/
    - reject:   POST /api/v1/sos/reports/{id}/reject/
    - escalate: POST /api/v1/sos/reports/{id}/escalate/
    - resolve:  POST /api/v1/sos/reports/{id}/resolve/
    """

    http_method_names = ["get", "post", "head", "options"]

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsVerifiedMember()]
        return [IsAuthenticated(), IsVerifiedMember()]

    def get_queryset(self):
        """
        Return reports visible to the current user:
        - Reports the user submitted
        - Reports assigned to the user (if they are a leader)
        """
        user = self.request.user
        queryset = SOSReport.objects.select_related(
            "reporter",
            "assigned_to",
        ).prefetch_related("escalations__escalated_by")

        queryset = queryset.filter(
            Q(reporter=user) | Q(assigned_to=user)
        )

        # Filters
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        level_filter = self.request.query_params.get("escalation_level")
        if level_filter:
            queryset = queryset.filter(escalation_level=level_filter)

        return queryset.order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "create":
            return SOSReportCreateSerializer
        if self.action == "list":
            return SOSReportListSerializer
        return SOSReportDetailSerializer

    def perform_create(self, serializer):
        """Create report and fire auto-assignment task."""
        from .tasks import assign_sos_to_atistavi

        report = serializer.save(reporter=self.request.user)
        assign_sos_to_atistavi.delay(report.id)

    @action(detail=True, methods=["post"])
    def verify(self, request, pk=None):
        """
        Atistavi verifies the SOS report as legitimate.

        Permissions: IsAtistavi + must be assigned handler + status must be 'pending'
        """
        report = self.get_object()

        # Must be an atistavi
        if not IsAtistavi().has_permission(request, self):
            return Response(
                {"detail": "Only an atistavi can verify SOS reports."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Must be the assigned handler
        if report.assigned_to != request.user:
            return Response(
                {"detail": "You are not the assigned handler for this report."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Must be in pending status
        if report.status != SOSReport.Status.PENDING:
            return Response(
                {"detail": f"Cannot verify a report with status '{report.status}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        report.status = SOSReport.Status.VERIFIED
        report.save(update_fields=["status", "updated_at"])

        serializer = SOSReportDetailSerializer(report, context=self.get_serializer_context())
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """
        Handler rejects the SOS report as false or spam.

        Permissions: Must be assigned handler + report in pending/verified status.
        """
        report = self.get_object()

        if report.assigned_to != request.user:
            return Response(
                {"detail": "You are not the assigned handler for this report."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if report.status not in [SOSReport.Status.PENDING, SOSReport.Status.VERIFIED]:
            return Response(
                {"detail": f"Cannot reject a report with status '{report.status}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        report.status = SOSReport.Status.REJECTED
        report.save(update_fields=["status", "updated_at"])

        serializer = SOSReportDetailSerializer(report, context=self.get_serializer_context())
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def escalate(self, request, pk=None):
        """
        Handler escalates the report to the next governance tier.

        Permissions: Must be assigned handler + status must be 'verified'.
        Request body: {"note": "optional reason"}
        """
        report = self.get_object()

        if report.assigned_to != request.user:
            return Response(
                {"detail": "You are not the assigned handler for this report."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if report.status != SOSReport.Status.VERIFIED:
            return Response(
                {"detail": "Only verified reports can be escalated."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        next_level = report.get_next_escalation_level()
        if next_level is None:
            return Response(
                {"detail": "Report is already at the maximum escalation level."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from_level = report.escalation_level
        new_leader = report.find_leader_at_next_level()
        note = request.data.get("note", "")

        # Create escalation audit record
        SOSEscalation.objects.create(
            report=report,
            from_level=from_level,
            to_level=next_level,
            escalated_by=request.user,
            note=note,
        )

        # Update report
        report.escalation_level = next_level
        report.status = SOSReport.Status.ESCALATED
        report.assigned_to = new_leader
        report.save(update_fields=["escalation_level", "status", "assigned_to", "updated_at"])

        serializer = SOSReportDetailSerializer(report, context=self.get_serializer_context())
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        """
        Handler marks the report as resolved.

        Permissions: Must be assigned handler + status in (verified, escalated).
        """
        report = self.get_object()

        if report.assigned_to != request.user:
            return Response(
                {"detail": "You are not the assigned handler for this report."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if report.status not in [SOSReport.Status.VERIFIED, SOSReport.Status.ESCALATED]:
            return Response(
                {"detail": f"Cannot resolve a report with status '{report.status}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        report.status = SOSReport.Status.RESOLVED
        report.resolved_at = timezone.now()
        report.save(update_fields=["status", "resolved_at", "updated_at"])

        serializer = SOSReportDetailSerializer(report, context=self.get_serializer_context())
        return Response(serializer.data)
