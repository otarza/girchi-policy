from django.core.cache import cache
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import IsOnboarded

CACHE_TTL_PROGRESS = 60 * 5  # 5 minutes

from .models import TerritoryProgress, TierCapability
from .serializers import TerritoryProgressSerializer, TierCapabilitySerializer


@extend_schema(tags=["Gamification"], summary="Get my precinct's territory progress")
class MyProgressView(APIView):
    """
    GET /api/v1/gamification/progress/

    Returns territory progress for the authenticated user's precinct.
    """

    permission_classes = [IsAuthenticated, IsOnboarded]

    def get(self, request):
        precinct = request.user.precinct
        if not precinct:
            return Response(
                {"error": "NO_PRECINCT", "message": "You have not been assigned to a precinct yet."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cache_key = f"gamification:progress:{precinct.id}"
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        progress, _ = TerritoryProgress.objects.get_or_create(precinct=precinct)
        serializer = TerritoryProgressSerializer(progress)
        cache.set(cache_key, serializer.data, CACHE_TTL_PROGRESS)
        return Response(serializer.data)


@extend_schema(tags=["Gamification"], summary="Get territory progress for a specific precinct")
class PrecinctProgressView(APIView):
    """
    GET /api/v1/gamification/progress/{precinct_id}/

    Returns territory progress for a specific precinct (public, auth required).
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, precinct_id):
        from apps.territories.models import Precinct

        try:
            precinct = Precinct.objects.get(pk=precinct_id)
        except Precinct.DoesNotExist:
            return Response(
                {"error": "NOT_FOUND", "message": "Precinct not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        cache_key = f"gamification:progress:{precinct_id}"
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        progress, _ = TerritoryProgress.objects.get_or_create(precinct=precinct)
        serializer = TerritoryProgressSerializer(progress)
        cache.set(cache_key, serializer.data, CACHE_TTL_PROGRESS)
        return Response(serializer.data)


@extend_schema(tags=["Gamification"], summary="List all tier capabilities grouped by tier")
class CapabilitiesView(APIView):
    """
    GET /api/v1/gamification/capabilities/

    Returns all capabilities grouped by tier.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        capabilities = TierCapability.objects.all().order_by("tier", "key")
        # Group by tier
        result = {}
        for cap in capabilities:
            tier_key = str(cap.tier)
            if tier_key not in result:
                result[tier_key] = []
            result[tier_key].append(TierCapabilitySerializer(cap).data)
        return Response(result)


@extend_schema(tags=["Gamification"], summary="List capabilities unlocked for my precinct's tier")
class UnlockedCapabilitiesView(APIView):
    """
    GET /api/v1/gamification/capabilities/unlocked/

    Returns capabilities unlocked for the authenticated user's precinct.
    """

    permission_classes = [IsAuthenticated, IsOnboarded]

    def get(self, request):
        precinct = request.user.precinct
        if not precinct:
            return Response([])

        progress, _ = TerritoryProgress.objects.get_or_create(precinct=precinct)
        caps = TierCapability.objects.filter(tier__lte=progress.current_tier).order_by("tier", "key")
        serializer = TierCapabilitySerializer(caps, many=True)
        return Response(serializer.data)
