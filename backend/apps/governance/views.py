from django.core.cache import cache
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

CACHE_TTL_HIERARCHY = 60 * 10       # 10 minutes
CACHE_TTL_ELECTION_RESULTS = None   # indefinite for completed elections

from common.permissions import IsActiveMember, IsNotDiaspora, IsOnboarded, IsVerifiedMember

from .models import Candidacy, Election, ElectionStatus, Vote
from .serializers import (
    CandidacySerializer,
    ElectionCreateSerializer,
    ElectionDetailSerializer,
    ElectionListSerializer,
    ElectionResultsSerializer,
    VoteSerializer,
)


@extend_schema_view(
    list=extend_schema(tags=["Governance"], summary="List elections", parameters=[
        OpenApiParameter("status", str, description="Filter by status (nomination/voting/completed/cancelled)"),
        OpenApiParameter("election_type", str, description="Filter by type (atistavi/hierarchy/parliamentary)"),
        OpenApiParameter("position_id", int, description="Filter by position ID"),
    ]),
    retrieve=extend_schema(tags=["Governance"], summary="Get election detail"),
    create=extend_schema(tags=["Governance"], summary="Create an election"),
)
class ElectionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Election CRUD operations and election lifecycle actions.

    Permissions:
    - List/Retrieve: IsAuthenticated
    - Create: IsAuthenticated + IsOnboarded (later: IsLeaderAtTier)
    - Nominate: IsAuthenticated + IsActiveMember + IsNotDiaspora
    - Vote: IsAuthenticated + IsVerifiedMember + IsNotDiaspora
    - Results: IsAuthenticated

    Actions:
    - list: GET /api/v1/governance/elections/
    - retrieve: GET /api/v1/governance/elections/{id}/
    - create: POST /api/v1/governance/elections/
    - nominate: POST /api/v1/governance/elections/{id}/nominate/
    - vote: POST /api/v1/governance/elections/{id}/vote/
    - results: GET /api/v1/governance/elections/{id}/results/
    """

    permission_classes = [IsAuthenticated, IsOnboarded]

    def get_queryset(self):
        """
        Return elections with optimizations and optional filtering.
        Annotates with candidate_count and vote_count for list view.
        """
        queryset = Election.objects.select_related(
            "position__group",
            "position__precinct",
            "position__district",
            "created_by",
        ).prefetch_related("candidacies", "votes")

        # Annotate counts for list view
        queryset = queryset.annotate(
            candidate_count=Count("candidacies", filter=Q(candidacies__is_approved=True)),
            vote_count=Count("votes"),
        )

        # Filter by status if provided
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by election type if provided
        type_filter = self.request.query_params.get("election_type")
        if type_filter:
            queryset = queryset.filter(election_type=type_filter)

        # Filter by position if provided
        position_id = self.request.query_params.get("position_id")
        if position_id:
            queryset = queryset.filter(position_id=position_id)

        return queryset.order_by("-created_at")

    def get_serializer_class(self):
        """Return different serializers for different actions."""
        if self.action == "list":
            return ElectionListSerializer
        elif self.action == "create":
            return ElectionCreateSerializer
        elif self.action == "results":
            return ElectionResultsSerializer
        return ElectionDetailSerializer

    def get_permissions(self):
        """Override permissions for specific actions."""
        if self.action == "nominate":
            return [IsAuthenticated(), IsActiveMember(), IsNotDiaspora()]
        elif self.action == "vote":
            return [IsAuthenticated(), IsVerifiedMember(), IsNotDiaspora()]
        return super().get_permissions()

    def perform_create(self, serializer):
        """Set created_by to current user."""
        serializer.save(created_by=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """
        Get election detail with candidacies.
        Annotate candidacies with vote_count.
        """
        election = self.get_object()

        # Annotate candidacies with vote counts
        candidacies = election.candidacies.annotate(vote_count=Count("votes"))

        # Manually set the annotated candidacies on the election
        election.candidacies_with_counts = candidacies

        # Calculate total votes
        total_votes = election.votes.count()

        serializer = self.get_serializer(election)
        data = serializer.data
        data["total_votes"] = total_votes

        # Replace candidacies with annotated version
        data["candidacies"] = CandidacySerializer(
            candidacies, many=True, context=self.get_serializer_context()
        ).data

        return Response(data)

    @extend_schema(tags=["Governance"], summary="Register as candidate")
    @action(detail=True, methods=["post"])
    def nominate(self, request, pk=None):
        """
        Register as candidate in an election.

        Business rules:
        - Election must be in NOMINATION status
        - Current time must be within nomination period
        - User must be an eligible candidate (checked via position.get_eligible_candidates())
        - User can only nominate once per election (UniqueConstraint enforced)

        Request body:
        {
            "statement": "Optional candidate statement"
        }
        """
        election = self.get_object()
        user = request.user

        # Check election status
        if election.status != ElectionStatus.NOMINATION:
            return Response(
                {"detail": "Election is not in nomination period."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if nomination period is active
        if not election.is_nomination_period:
            return Response(
                {"detail": "Nomination period has not started or has ended."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if user is eligible candidate
        eligible_candidates = election.get_eligible_candidates()
        if user not in eligible_candidates:
            # Provide election-type-specific error messages
            from .models import ElectionType, GovernanceTier
            from apps.accounts.models import User as UserModel

            if election.election_type == ElectionType.PARLIAMENTARY:
                if user.role != UserModel.Role.GEDER:
                    message = "Only GeDers can run in parliamentary elections."
                elif user.member_status != UserModel.MemberStatus.ACTIVE:
                    message = "Only active members can run in parliamentary elections."
                else:
                    message = "You are not eligible to run in this election."
            else:
                # Tier-specific messages for hierarchy elections
                tier = election.position.tier if election.position else None
                if tier == GovernanceTier.ATISTAVI:
                    message = "Only active members in this group can run for atistavi."
                elif tier == GovernanceTier.FIFTY:
                    message = "Only atistavis in this precinct can run for fifty-leader."
                elif tier == GovernanceTier.HUNDRED:
                    message = "Only fifty-leaders in this district can run for hundred-leader."
                elif tier == GovernanceTier.THOUSAND:
                    message = "Only hundred-leaders can run for thousand-leader."
                else:
                    message = "You are not eligible to run for this position."

            return Response(
                {"detail": message},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Create candidacy
        statement = request.data.get("statement", "")

        try:
            candidacy = Candidacy.objects.create(
                election=election, candidate=user, statement=statement
            )
        except Exception as e:
            # UniqueConstraint will raise IntegrityError
            return Response(
                {"detail": "You have already registered for this election."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = CandidacySerializer(candidacy, context=self.get_serializer_context())
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(tags=["Governance"], summary="Cast a vote")
    @action(detail=True, methods=["post"])
    def vote(self, request, pk=None):
        """
        Cast vote in an election.

        Business rules:
        - Election must be in VOTING status
        - Current time must be within voting period
        - User must be an eligible voter (checked via position.get_eligible_voters())
        - Candidacy must belong to this election and be approved
        - User can only vote once per election (UniqueConstraint enforced)

        Request body:
        {
            "candidacy_id": 5
        }
        """
        election = self.get_object()
        user = request.user

        # Check election status
        if election.status != ElectionStatus.VOTING:
            return Response(
                {"detail": "Election is not in voting period."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if voting period is active
        if not election.is_voting_period:
            return Response(
                {"detail": "Voting period has not started or has ended."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if user is eligible voter
        eligible_voters = election.get_eligible_voters()
        if user not in eligible_voters:
            # Provide election-type-specific error messages
            from .models import ElectionType, GovernanceTier
            from apps.accounts.models import User as UserModel

            if election.election_type == ElectionType.PARLIAMENTARY:
                if user.role != UserModel.Role.GEDER:
                    message = "Only GeDers can vote in parliamentary elections."
                else:
                    message = "You are not eligible to vote in this election."
            else:
                # Tier-specific messages for hierarchy elections
                tier = election.position.tier if election.position else None
                if tier == GovernanceTier.ATISTAVI:
                    message = "Only verified members in this group can vote for atistavis."
                elif tier == GovernanceTier.FIFTY:
                    message = "Only atistavis in this precinct can vote for fifty-leaders."
                elif tier == GovernanceTier.HUNDRED:
                    message = "Only fifty-leaders in this district can vote for hundred-leaders."
                elif tier == GovernanceTier.THOUSAND:
                    message = "Only hundred-leaders can vote for thousand-leaders."
                else:
                    message = "You are not eligible to vote in this election."

            return Response(
                {"detail": message},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Get candidacy from request
        candidacy_id = request.data.get("candidacy_id")
        if not candidacy_id:
            return Response(
                {"detail": "candidacy_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Verify candidacy belongs to this election and is approved
        candidacy = get_object_or_404(
            Candidacy, id=candidacy_id, election=election, is_approved=True
        )

        # Cast vote
        try:
            vote = Vote.objects.create(
                election=election, voter=user, candidacy=candidacy
            )
        except Exception as e:
            # UniqueConstraint will raise IntegrityError
            return Response(
                {"detail": "You have already voted in this election."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = VoteSerializer(vote, context=self.get_serializer_context())
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(tags=["Governance"], summary="Get election results")
    @action(detail=True, methods=["get"])
    def results(self, request, pk=None):
        """
        Get election results with vote tallies.

        Returns:
        - election_id, status
        - winner: candidacy with highest vote count
        - results: array of all candidacies with vote counts (sorted by votes descending)
        - total_votes: total number of votes cast
        - total_eligible_voters: count of eligible voters

        Completed elections are cached indefinitely (results never change after completion).
        """
        election = self.get_object()

        # Serve from cache for completed elections
        if election.status == ElectionStatus.COMPLETED:
            cache_key = f"election:results:{election.id}"
            cached = cache.get(cache_key)
            if cached is not None:
                return Response(cached)

        # Annotate candidacies with vote counts and order by vote count
        candidacies = (
            election.candidacies.filter(is_approved=True)
            .annotate(vote_count=Count("votes"))
            .order_by("-vote_count")
        )

        # Get winner (first in ordered list)
        winner = candidacies.first() if candidacies.exists() else None

        # Calculate total votes
        total_votes = election.votes.count()

        # Calculate total eligible voters
        total_eligible_voters = election.get_eligible_voters().count()

        # Prepare results data
        results_data = {
            "election_id": election.id,
            "status": election.status,
            "winner": winner,
            "results": candidacies,
            "total_votes": total_votes,
            "total_eligible_voters": total_eligible_voters,
        }

        serializer = ElectionResultsSerializer(results_data, context=self.get_serializer_context())

        # Cache completed election results indefinitely
        if election.status == ElectionStatus.COMPLETED:
            cache.set(f"election:results:{election.id}", serializer.data, CACHE_TTL_ELECTION_RESULTS)

        return Response(serializer.data)

    @extend_schema(tags=["Governance"], summary="Transition election to voting phase")
    @action(detail=True, methods=["post"])
    def start_voting(self, request, pk=None):
        """
        Manually transition election to voting status.

        Useful for testing or admin control.
        Permissions: IsAuthenticated (for now; later can add IsAdminUser)

        Business rules:
        - Election must be in NOMINATION status
        - Current time must be >= voting_start
        """
        election = self.get_object()

        try:
            election.transition_to_voting()
        except ValueError as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(election)
        return Response(serializer.data)

    @extend_schema(tags=["Governance"], summary="Complete election and tally votes")
    @action(detail=True, methods=["post"])
    def complete_election(self, request, pk=None):
        """
        Manually transition election to completed and trigger vote tallying.

        Useful for testing or admin control.
        Permissions: IsAuthenticated (for now; later can add IsAdminUser)

        Business rules:
        - Election must be in VOTING status
        - Current time must be >= voting_end
        - Triggers tally_election_results Celery task asynchronously
        """
        election = self.get_object()

        try:
            election.transition_to_completed()

            # Trigger vote tallying asynchronously
            from .tasks import tally_election_results

            tally_election_results.delay(election.id)
        except ValueError as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(election)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(tags=["Governance"], summary="List leadership positions", parameters=[
        OpenApiParameter("tier", int, description="Filter by tier (10/50/100/1000)"),
        OpenApiParameter("precinct_id", int, description="Filter by precinct"),
        OpenApiParameter("district_id", int, description="Filter by district"),
        OpenApiParameter("is_active", bool, description="Filter active/inactive"),
        OpenApiParameter("is_vacant", bool, description="Filter vacant positions"),
    ]),
    retrieve=extend_schema(tags=["Governance"], summary="Get position detail"),
)
class LeaderPositionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for LeaderPosition list and detail operations.

    Permissions:
    - List/Retrieve: IsAuthenticated

    Query parameters:
    - tier: Filter by governance tier (10, 50, 100, 1000)
    - precinct_id: Filter positions in a specific precinct
    - district_id: Filter positions in a specific district
    - is_active: Filter active/inactive positions (true/false)
    - is_vacant: Filter vacant positions (true/false)

    Actions:
    - list: GET /api/v1/governance/positions/
    - retrieve: GET /api/v1/governance/positions/{id}/
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return positions with optimizations and optional filtering.
        """
        queryset = LeaderPosition.objects.select_related(
            "group",
            "precinct__district__region",
            "district__region",
            "holder",
            "parent",
        )

        # Filter by tier
        tier_filter = self.request.query_params.get("tier")
        if tier_filter:
            queryset = queryset.filter(tier=tier_filter)

        # Filter by precinct
        precinct_id = self.request.query_params.get("precinct_id")
        if precinct_id:
            queryset = queryset.filter(precinct_id=precinct_id)

        # Filter by district
        district_id = self.request.query_params.get("district_id")
        if district_id:
            queryset = queryset.filter(district_id=district_id)

        # Filter by is_active
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            # Convert string to boolean
            is_active_bool = is_active.lower() == "true"
            queryset = queryset.filter(is_active=is_active_bool)

        # Filter by is_vacant (holder is null)
        is_vacant = self.request.query_params.get("is_vacant")
        if is_vacant is not None:
            is_vacant_bool = is_vacant.lower() == "true"
            if is_vacant_bool:
                queryset = queryset.filter(holder__isnull=True)
            else:
                queryset = queryset.filter(holder__isnull=False)

        return queryset.order_by("tier", "-created_at")

    def get_serializer_class(self):
        """Return different serializers for different actions."""
        if self.action == "list":
            from .serializers import LeaderPositionListSerializer

            return LeaderPositionListSerializer
        from .serializers import LeaderPositionDetailSerializer

        return LeaderPositionDetailSerializer


@extend_schema(
    tags=["Governance"],
    summary="Get governance hierarchy tree",
    parameters=[
        OpenApiParameter("district_id", int, description="Filter to district (shows 100→50→10)"),
        OpenApiParameter("precinct_id", int, description="Filter to precinct (shows 50→10)"),
        OpenApiParameter("max_depth", int, description="Max tree depth 1-4 (default 4)"),
    ],
)
class HierarchyTreeView(APIView):
    """
    View for governance hierarchy tree.

    GET /api/v1/governance/hierarchy/

    Query parameters:
    - district_id: Filter to specific district (shows 100→50→10)
    - precinct_id: Filter to specific precinct (shows 50→10)
    - max_depth: Maximum tree depth (1-4, default=4)

    Returns nested tree structure.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        from .models import GovernanceTier, LeaderPosition
        from .serializers import HierarchyNodeSerializer

        district_id = request.query_params.get("district_id")
        precinct_id = request.query_params.get("precinct_id")

        # Try cache first
        cache_key = f"hierarchy:{district_id or 'all'}:{precinct_id or 'all'}"
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        # Determine starting tier based on filters
        if precinct_id:
            # Precinct level: start from tier=50
            queryset = LeaderPosition.objects.filter(
                tier=GovernanceTier.FIFTY,
                precinct_id=precinct_id,
                is_active=True,
            )
            start_tier = "50 (Precinct)"
        elif district_id:
            # District level: start from tier=100
            queryset = LeaderPosition.objects.filter(
                tier=GovernanceTier.HUNDRED,
                district_id=district_id,
                is_active=True,
            )
            start_tier = "100 (District)"
        else:
            # Party-wide: start from tier=1000
            queryset = LeaderPosition.objects.filter(
                tier=GovernanceTier.THOUSAND, is_active=True
            )
            start_tier = "1000 (Council)"

        # Optimize query
        queryset = queryset.select_related(
            "holder", "district", "precinct", "group", "parent"
        )

        # Get max depth
        max_depth_param = request.query_params.get("max_depth", "4")
        try:
            max_depth = int(max_depth_param)
            max_depth = min(max(max_depth, 1), 4)  # Clamp to 1-4
        except ValueError:
            max_depth = 4

        # Serialize with recursive children
        context = {
            "include_children": True,
            "max_depth": max_depth,
            "current_depth": 0,
        }

        serializer = HierarchyNodeSerializer(queryset, many=True, context=context)

        response_data = {
            "start_tier": start_tier,
            "hierarchy": serializer.data,
            "filters": {
                "district_id": district_id,
                "precinct_id": precinct_id,
                "max_depth": max_depth,
            },
            "total_positions": queryset.count(),
        }

        cache.set(cache_key, response_data, CACHE_TTL_HIERARCHY)
        return Response(response_data)
