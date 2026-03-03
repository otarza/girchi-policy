from django.db.models import Count
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.permissions import IsLeaderAtTier, IsVerifiedMember

from .models import Initiative, InitiativeSignature
from .serializers import (
    InitiativeCreateSerializer,
    InitiativeDetailSerializer,
    InitiativeListSerializer,
)


@extend_schema_view(
    list=extend_schema(tags=["Initiatives"], summary="List initiatives/petitions", parameters=[
        OpenApiParameter("status", str, description="Filter by status (open/threshold_met/responded/closed)"),
        OpenApiParameter("precinct_id", int, description="Filter by precinct"),
        OpenApiParameter("district_id", int, description="Filter by district"),
    ]),
    retrieve=extend_schema(tags=["Initiatives"], summary="Get initiative detail"),
    create=extend_schema(tags=["Initiatives"], summary="Create a new initiative/petition"),
)
class InitiativeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Initiative CRUD and signature actions.

    Actions:
    - list:     GET    /api/v1/initiatives/
    - retrieve: GET    /api/v1/initiatives/{id}/
    - create:   POST   /api/v1/initiatives/
    - sign:     POST   /api/v1/initiatives/{id}/sign/
    - unsign:   DELETE /api/v1/initiatives/{id}/sign/
    - respond:  POST   /api/v1/initiatives/{id}/respond/
    """

    http_method_names = ["get", "post", "delete", "head", "options"]
    permission_classes = [IsAuthenticated, IsVerifiedMember]

    def get_queryset(self):
        """Return initiatives annotated with signature_count."""
        queryset = Initiative.objects.select_related(
            "author",
            "precinct",
            "district",
            "responded_by",
        ).annotate(signature_count=Count("signatures"))

        # Filters
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        precinct_id = self.request.query_params.get("precinct_id")
        if precinct_id:
            queryset = queryset.filter(precinct_id=precinct_id)

        district_id = self.request.query_params.get("district_id")
        if district_id:
            queryset = queryset.filter(district_id=district_id)

        return queryset.order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "create":
            return InitiativeCreateSerializer
        if self.action == "list":
            return InitiativeListSerializer
        return InitiativeDetailSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @extend_schema(tags=["Initiatives"], summary="Sign an initiative")
    @action(detail=True, methods=["post"])
    def sign(self, request, pk=None):
        """
        Sign the initiative. One signature per user per initiative.

        Permissions: IsVerifiedMember
        """
        initiative = self.get_object()

        if initiative.status not in [
            Initiative.Status.OPEN,
            Initiative.Status.THRESHOLD_MET,
        ]:
            return Response(
                {"detail": "Cannot sign a closed or responded initiative."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if already signed
        if InitiativeSignature.objects.filter(
            initiative=initiative, signer=request.user
        ).exists():
            return Response(
                {"detail": "You have already signed this initiative."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        InitiativeSignature.objects.create(
            initiative=initiative,
            signer=request.user,
        )

        # Refresh with signature count annotation
        initiative.refresh_from_db()
        initiative.signature_count = initiative.signatures.count()

        serializer = InitiativeDetailSerializer(
            initiative, context=self.get_serializer_context()
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @sign.mapping.delete
    def unsign(self, request, pk=None):
        """
        Withdraw signature from the initiative.

        Permissions: IsVerifiedMember (own signature only)
        """
        initiative = self.get_object()

        try:
            sig = InitiativeSignature.objects.get(
                initiative=initiative, signer=request.user
            )
            sig.delete()
        except InitiativeSignature.DoesNotExist:
            return Response(
                {"detail": "You have not signed this initiative."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(tags=["Initiatives"], summary="Official leader response to initiative (50+ leader)")
    @action(detail=True, methods=["post"])
    def respond(self, request, pk=None):
        """
        Territory leader provides official response to a threshold-met initiative.

        Permissions: IsLeaderAtTier(50) + initiative.status == 'threshold_met'
        Request body: {"response_text": "..."}
        """
        # Check leader permission
        if not IsLeaderAtTier(50).has_permission(request, self):
            return Response(
                {"detail": "Only a fifty-leader or higher can respond to initiatives."},
                status=status.HTTP_403_FORBIDDEN,
            )

        initiative = self.get_object()

        if initiative.status != Initiative.Status.THRESHOLD_MET:
            return Response(
                {"detail": "Only threshold-met initiatives can be responded to."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_text = request.data.get("response_text", "").strip()
        if not response_text:
            return Response(
                {"detail": "response_text is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        initiative.response_text = response_text
        initiative.responded_by = request.user
        initiative.responded_at = timezone.now()
        initiative.status = Initiative.Status.RESPONDED
        initiative.save(
            update_fields=["response_text", "responded_by", "responded_at", "status", "updated_at"]
        )

        initiative.signature_count = initiative.signatures.count()
        serializer = InitiativeDetailSerializer(
            initiative, context=self.get_serializer_context()
        )
        return Response(serializer.data)
