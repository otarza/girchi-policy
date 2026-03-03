from django.db.models import Q
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.permissions import IsLeaderAtTier, IsVerifiedMember

from .models import ArbitrationCase
from .serializers import (
    ArbitrationCaseCreateSerializer,
    ArbitrationCaseDetailSerializer,
    ArbitrationCaseListSerializer,
)


@extend_schema_view(
    list=extend_schema(tags=["Arbitration"], summary="List arbitration cases (own + arbitrating)", parameters=[
        OpenApiParameter("status", str, description="Filter by status"),
        OpenApiParameter("case_type", str, description="Filter by case type"),
        OpenApiParameter("tier", int, description="Filter by tier"),
    ]),
    retrieve=extend_schema(tags=["Arbitration"], summary="Get case detail"),
    create=extend_schema(tags=["Arbitration"], summary="File a new arbitration case"),
)
class ArbitrationCaseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Arbitration Case CRUD and lifecycle actions.

    Actions:
    - list:     GET  /api/v1/arbitration/cases/
    - retrieve: GET  /api/v1/arbitration/cases/{id}/
    - create:   POST /api/v1/arbitration/cases/
    - decide:   POST /api/v1/arbitration/cases/{id}/decide/
    - appeal:   POST /api/v1/arbitration/cases/{id}/appeal/
    - claim:    POST /api/v1/arbitration/cases/{id}/claim/
    """

    http_method_names = ["get", "post", "head", "options"]
    permission_classes = [IsAuthenticated, IsVerifiedMember]

    def get_queryset(self):
        """
        Return cases visible to the current user:
        - Cases filed by the user (complainant)
        - Cases filed against the user (respondent)
        - Cases assigned to the user as arbitrator
        """
        user = self.request.user
        queryset = ArbitrationCase.objects.select_related(
            "complainant",
            "respondent",
            "arbitrator",
            "related_endorsement",
        ).filter(
            Q(complainant=user) | Q(respondent=user) | Q(arbitrator=user)
        )

        # Filters
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        case_type_filter = self.request.query_params.get("case_type")
        if case_type_filter:
            queryset = queryset.filter(case_type=case_type_filter)

        tier_filter = self.request.query_params.get("tier")
        if tier_filter:
            queryset = queryset.filter(tier=tier_filter)

        return queryset.order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "create":
            return ArbitrationCaseCreateSerializer
        if self.action == "list":
            return ArbitrationCaseListSerializer
        return ArbitrationCaseDetailSerializer

    def perform_create(self, serializer):
        """Auto-set tier based on case_type."""
        case_type = serializer.validated_data.get("case_type")
        tier = ArbitrationCase.get_initial_tier(case_type)
        serializer.save(complainant=self.request.user, tier=tier)

    @extend_schema(tags=["Arbitration"], summary="Claim a case as arbitrator")
    @action(detail=True, methods=["post"])
    def claim(self, request, pk=None):
        """
        Leader claims a case to become its arbitrator.

        Permissions: IsLeaderAtTier(case.tier) + case.status == 'submitted'
        """
        case = self.get_object()

        if not IsLeaderAtTier(case.tier).has_permission(request, self):
            return Response(
                {"detail": f"Must be a leader at tier {case.tier} or higher to claim this case."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if case.status != ArbitrationCase.Status.SUBMITTED:
            return Response(
                {"detail": f"Cannot claim a case with status '{case.status}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if case.arbitrator:
            return Response(
                {"detail": "This case already has an assigned arbitrator."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Cannot claim your own case
        if case.complainant == request.user or case.respondent == request.user:
            return Response(
                {"detail": "You cannot arbitrate a case you are a party to."},
                status=status.HTTP_403_FORBIDDEN,
            )

        case.arbitrator = request.user
        case.status = ArbitrationCase.Status.UNDER_REVIEW
        case.save(update_fields=["arbitrator", "status", "updated_at"])

        serializer = ArbitrationCaseDetailSerializer(
            case, context=self.get_serializer_context()
        )
        return Response(serializer.data)

    @extend_schema(tags=["Arbitration"], summary="Render arbitration decision")
    @action(detail=True, methods=["post"])
    def decide(self, request, pk=None):
        """
        Arbitrator renders a decision on the case.

        Permissions: IsLeaderAtTier(case.tier) + arbitrator == request.user
        Request body:
        {
            "decision_text": "...",
            "apply_endorsement_penalty": true  (optional, for endorsement_fraud cases)
        }
        """
        case = self.get_object()

        # Must be the assigned arbitrator
        if case.arbitrator != request.user:
            return Response(
                {"detail": "Only the assigned arbitrator can render a decision."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Verify still holds required tier
        if not IsLeaderAtTier(case.tier).has_permission(request, self):
            return Response(
                {"detail": f"Must hold a tier {case.tier}+ position to decide this case."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if case.status != ArbitrationCase.Status.UNDER_REVIEW:
            return Response(
                {"detail": f"Cannot decide a case with status '{case.status}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        decision_text = request.data.get("decision_text", "").strip()
        if not decision_text:
            return Response(
                {"detail": "decision_text is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        case.decision_text = decision_text
        case.decided_at = timezone.now()
        case.status = ArbitrationCase.Status.DECIDED
        case.save(update_fields=["decision_text", "decided_at", "status", "updated_at"])

        # Apply endorsement penalties if requested for fraud cases
        apply_penalty = request.data.get("apply_endorsement_penalty", False)
        if (
            apply_penalty
            and case.case_type == ArbitrationCase.CaseType.ENDORSEMENT_FRAUD
            and case.related_endorsement
        ):
            from .tasks import apply_endorsement_penalties

            apply_endorsement_penalties.delay(case.id)

        serializer = ArbitrationCaseDetailSerializer(
            case, context=self.get_serializer_context()
        )
        return Response(serializer.data)

    @extend_schema(tags=["Arbitration"], summary="Appeal decision to next tier")
    @action(detail=True, methods=["post"])
    def appeal(self, request, pk=None):
        """
        Complainant or respondent appeals the decision to the next tier.

        Permissions: Must be complainant or respondent + case.status == 'decided'
        Request body: {"appeal_reason": "..."}
        """
        case = self.get_object()

        # Must be a party to the case
        if request.user not in (case.complainant, case.respondent):
            return Response(
                {"detail": "Only the complainant or respondent can appeal."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if case.status != ArbitrationCase.Status.DECIDED:
            return Response(
                {"detail": "Only decided cases can be appealed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        next_tier = case.next_appeal_tier
        if next_tier is None:
            return Response(
                {"detail": "This case has reached the maximum appeal tier (Council)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        appeal_reason = request.data.get("appeal_reason", "").strip()
        if not appeal_reason:
            return Response(
                {"detail": "appeal_reason is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Promote to next tier, reset arbitrator, append reason to description
        case.tier = next_tier
        case.status = ArbitrationCase.Status.APPEALED
        case.arbitrator = None
        case.description = (
            f"{case.description}\n\n"
            f"--- Appeal by {request.user.get_full_name() or request.user.phone_number} ---\n"
            f"{appeal_reason}"
        )
        case.save(update_fields=["tier", "status", "arbitrator", "description", "updated_at"])

        serializer = ArbitrationCaseDetailSerializer(
            case, context=self.get_serializer_context()
        )
        return Response(serializer.data)
