from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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
        eligible_candidates = election.position.get_eligible_candidates()
        if user not in eligible_candidates:
            # Provide tier-specific error messages
            from .models import GovernanceTier

            tier = election.position.tier
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
        eligible_voters = election.position.get_eligible_voters()
        if user not in eligible_voters:
            # Provide tier-specific error messages
            from .models import GovernanceTier

            tier = election.position.tier
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
        """
        election = self.get_object()

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
        total_eligible_voters = election.position.get_eligible_voters().count()

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
        return Response(serializer.data)

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
