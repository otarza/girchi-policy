from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from common.permissions import IsOnboarded, IsGeDer, IsVerifiedMember, IsNotDiaspora
from .models import GroupOfTen, Membership
from .serializers import (
    GroupOfTenSerializer,
    GroupOfTenListSerializer,
    MembershipSerializer,
)


class GroupOfTenViewSet(viewsets.ModelViewSet):
    """
    ViewSet for GroupOfTen CRUD operations.

    Permissions:
    - List/Retrieve: IsAuthenticated + IsOnboarded + IsVerifiedMember
    - Create: IsAuthenticated + IsOnboarded + IsGeDer + IsNotDiaspora
    - Join/Leave: IsAuthenticated + IsOnboarded + IsVerifiedMember + IsNotDiaspora

    Business Rules:
    - GeDers can create groups in their own precinct
    - Cannot join full groups (is_full=True)
    - Can only be in one group at a time (OneToOne constraint)
    - GeDers join directly; Supporters need endorsement (enforced by IsVerifiedMember)
    """

    permission_classes = [IsAuthenticated, IsOnboarded, IsVerifiedMember]

    def get_queryset(self):
        """
        Annotate with member count and optionally filter by precinct.
        Uses select_related for performance optimization.
        """
        queryset = GroupOfTen.objects.select_related("precinct__district__region")
        queryset = queryset.annotate(
            member_count=Count("members", filter=Q(members__is_active=True))
        )

        # Filter by precinct if provided
        precinct_id = self.request.query_params.get("precinct_id")
        if precinct_id:
            queryset = queryset.filter(precinct_id=precinct_id)

        return queryset.order_by("-created_at")

    def get_serializer_class(self):
        """Use list serializer for list action, detail serializer otherwise."""
        if self.action == "list":
            return GroupOfTenListSerializer
        return GroupOfTenSerializer

    def get_permissions(self):
        """Override permissions for create and action-specific endpoints."""
        if self.action == "create":
            return [IsAuthenticated(), IsOnboarded(), IsGeDer(), IsNotDiaspora()]
        elif self.action in ["join", "leave"]:
            return [
                IsAuthenticated(),
                IsOnboarded(),
                IsVerifiedMember(),
                IsNotDiaspora(),
            ]
        return super().get_permissions()

    def perform_create(self, serializer):
        """
        Validate that user is creating group in their own precinct.
        """
        user = self.request.user
        precinct = serializer.validated_data.get("precinct")

        # Enforce "own precinct" rule if user has precinct assigned
        if user.precinct and user.precinct != precinct:
            raise serializers.ValidationError(
                {"precinct_id": "You can only create groups in your own precinct."}
            )

        serializer.save()

    @action(detail=True, methods=["post"])
    def join(self, request, pk=None):
        """
        Join a group. Creates or reactivates membership.

        Business rules:
        - Cannot join full groups (is_full=True)
        - Can only be in one group at a time (OneToOne constraint)
        - GeDers join directly; Supporters need endorsement (enforced by IsVerifiedMember)
        """
        group = self.get_object()
        user = request.user

        # Check if group is full
        if group.is_full:
            return Response(
                {"detail": "This group is full and cannot accept new members."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if user already has active membership
        if hasattr(user, "membership") and user.membership.is_active:
            return Response(
                {
                    "detail": "You are already a member of another group. Leave it first."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create or reactivate membership
        membership, created = Membership.objects.get_or_create(
            user=user, defaults={"group": group, "is_active": True}
        )

        if not created:
            # Reactivate existing membership
            membership.group = group
            membership.is_active = True
            membership.left_at = None
            membership.save(update_fields=["group", "is_active", "left_at"])

        # Update group full status
        group.update_full_status()

        serializer = MembershipSerializer(membership)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def leave(self, request, pk=None):
        """
        Leave a group. Marks membership as inactive.
        """
        group = self.get_object()
        user = request.user

        # Check if user is member of this group
        try:
            membership = Membership.objects.get(user=user, group=group, is_active=True)
        except Membership.DoesNotExist:
            return Response(
                {"detail": "You are not a member of this group."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Mark as inactive
        membership.is_active = False
        membership.left_at = timezone.now()
        membership.save(update_fields=["is_active", "left_at"])

        # Update group full status
        group.update_full_status()

        return Response({"detail": "You have left the group."}, status=status.HTTP_200_OK)
