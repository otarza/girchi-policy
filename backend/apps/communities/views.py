from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from common.permissions import IsOnboarded, IsGeDer, IsVerifiedMember, IsNotDiaspora
from .models import Endorsement, EndorsementQuota, GroupOfTen, Membership
from .serializers import (
    EndorsementSerializer,
    EndorsementQuotaSerializer,
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


class EndorsementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Endorsement operations.

    Permissions:
    - Create (endorse): IsAuthenticated + IsOnboarded + IsGeDer
    - List: IsAuthenticated + IsOnboarded
    - Delete (revoke): IsAuthenticated + IsOnboarded + IsGeDer (must be guarantor)

    Business Logic (GP-030):
    - On create: Check quota, check not suspended, promote supporter role to 'supporter'
    - On delete: Revert supporter role to 'unverified', remove from group, decrement used_slots
    """

    permission_classes = [IsAuthenticated, IsOnboarded]
    serializer_class = EndorsementSerializer

    def get_queryset(self):
        """
        Return endorsements where user is guarantor or supporter.
        """
        user = self.request.user
        return Endorsement.objects.filter(
            Q(guarantor=user) | Q(supporter=user)
        ).select_related("guarantor", "supporter")

    def get_permissions(self):
        """Override permissions for create action."""
        if self.action in ["create", "destroy"]:
            return [IsAuthenticated(), IsOnboarded(), IsGeDer()]
        return super().get_permissions()

    def perform_create(self, serializer):
        """
        Create endorsement with business logic (GP-030).

        Business rules:
        - Check quota exists and has remaining slots
        - Check guarantor is not suspended
        - Promote supporter role from 'unverified' to 'supporter'
        - Increment used_slots
        """
        guarantor = self.request.user
        supporter = serializer.validated_data["supporter"]

        # Validate guarantor has quota
        try:
            quota = EndorsementQuota.objects.get(geder=guarantor)
        except EndorsementQuota.DoesNotExist:
            raise serializers.ValidationError(
                {"detail": "Endorsement quota not found. Please contact support."}
            )

        # Check if suspended
        if quota.is_suspended:
            raise serializers.ValidationError(
                {
                    "detail": f"Your endorsement rights are suspended. Reason: {quota.suspended_reason}"
                }
            )

        # Check remaining slots
        if quota.remaining_slots <= 0:
            raise serializers.ValidationError(
                {
                    "detail": f"You have reached your endorsement limit ({quota.max_slots})."
                }
            )

        # Check if supporter already endorsed
        if hasattr(supporter, "endorsement"):
            existing = supporter.endorsement
            if existing.status == Endorsement.Status.ACTIVE:
                raise serializers.ValidationError(
                    {"supporter_id": "This user is already endorsed."}
                )

        # Check supporter is unverified
        if supporter.role != "unverified":
            raise serializers.ValidationError(
                {
                    "supporter_id": f"Can only endorse unverified users. This user's role is '{supporter.role}'."
                }
            )

        # Create endorsement
        endorsement = serializer.save(guarantor=guarantor, status=Endorsement.Status.ACTIVE)

        # Promote supporter role to 'supporter'
        supporter.role = "supporter"
        supporter.save(update_fields=["role"])

        # Increment used_slots
        quota.used_slots += 1
        quota.save(update_fields=["used_slots"])

    def perform_destroy(self, instance):
        """
        Revoke endorsement with business logic (GP-030).

        Business rules:
        - Only guarantor can revoke
        - Revert supporter role to 'unverified'
        - Remove supporter from group if active member
        - Decrement used_slots
        - Mark endorsement as revoked (soft delete)
        """
        guarantor = self.request.user

        # Verify user is the guarantor
        if instance.guarantor != guarantor:
            raise serializers.ValidationError(
                {"detail": "You can only revoke your own endorsements."}
            )

        # Revert supporter role to unverified
        supporter = instance.supporter
        supporter.role = "unverified"
        supporter.save(update_fields=["role"])

        # Remove from group if active member
        if hasattr(supporter, "membership") and supporter.membership.is_active:
            membership = supporter.membership
            membership.is_active = False
            membership.left_at = timezone.now()
            membership.save(update_fields=["is_active", "left_at"])

            # Update group full status
            membership.group.update_full_status()

        # Decrement used_slots
        quota = EndorsementQuota.objects.get(geder=guarantor)
        quota.used_slots = max(0, quota.used_slots - 1)
        quota.save(update_fields=["used_slots"])

        # Mark as revoked (soft delete - don't actually delete)
        instance.status = Endorsement.Status.REVOKED
        instance.revoked_at = timezone.now()
        instance.save(update_fields=["status", "revoked_at"])

    def destroy(self, request, *args, **kwargs):
        """Override destroy to use soft delete."""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "Endorsement revoked successfully."}, status=status.HTTP_200_OK
        )

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated, IsGeDer])
    def quota(self, request):
        """
        Check authenticated GeDer's endorsement quota.
        GET /api/v1/communities/endorsements/quota/
        """
        try:
            quota = EndorsementQuota.objects.get(geder=request.user)
        except EndorsementQuota.DoesNotExist:
            return Response(
                {"detail": "Endorsement quota not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = EndorsementQuotaSerializer(quota)
        return Response(serializer.data)
