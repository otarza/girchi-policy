import math

from django.core.cache import cache
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import filters, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.pagination import StandardPagination

from .models import District, Precinct, Region
from .serializers import (
    DistrictSerializer,
    PrecinctSerializer,
    PrecinctWithDistanceSerializer,
    RegionSerializer,
)

CACHE_TTL_TERRITORY = 60 * 60  # 1 hour


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance in kilometers between two lat/lon points using the Haversine formula.

    Args:
        lat1, lon1: Coordinates of first point
        lat2, lon2: Coordinates of second point

    Returns:
        Distance in kilometers
    """
    R = 6371  # Earth radius in kilometers

    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))

    return R * c


@extend_schema(tags=["Territories"], summary="List all regions")
class RegionListView(generics.ListAPIView):
    """
    List all regions in Georgia.

    Supports search by name (Georgian/English) and code.
    Cached for 1 hour (regions are static data).
    """

    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "name_ka", "code"]
    ordering_fields = ["name", "code"]

    def list(self, request, *args, **kwargs):
        # Only cache unfiltered requests
        if not request.query_params:
            cache_key = "territory:regions"
            cached = cache.get(cache_key)
            if cached is not None:
                return Response(cached)
            response = super().list(request, *args, **kwargs)
            cache.set(cache_key, response.data, CACHE_TTL_TERRITORY)
            return response
        return super().list(request, *args, **kwargs)


@extend_schema(tags=["Territories"], summary="List districts in a region")
class RegionDistrictsView(generics.ListAPIView):
    """
    List all districts for a specific region.

    Supports search by name (Georgian/English) and CEC code.
    Cached for 1 hour per region.
    """

    serializer_class = DistrictSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "name_ka", "cec_code"]
    ordering_fields = ["name"]

    def get_queryset(self):
        region_id = self.kwargs["pk"]
        return District.objects.filter(region_id=region_id).select_related("region")

    def list(self, request, *args, **kwargs):
        if not request.query_params:
            cache_key = f"territory:districts:{self.kwargs['pk']}"
            cached = cache.get(cache_key)
            if cached is not None:
                return Response(cached)
            response = super().list(request, *args, **kwargs)
            cache.set(cache_key, response.data, CACHE_TTL_TERRITORY)
            return response
        return super().list(request, *args, **kwargs)


@extend_schema(tags=["Territories"], summary="List precincts in a district")
class DistrictPrecinctsView(generics.ListAPIView):
    """
    List all precincts for a specific district.

    Supports search by name (Georgian/English) and CEC code.
    Cached for 1 hour per district.
    """

    serializer_class = PrecinctSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "name_ka", "cec_code"]
    ordering_fields = ["name"]

    def get_queryset(self):
        district_id = self.kwargs["pk"]
        return Precinct.objects.filter(district_id=district_id).select_related(
            "district__region"
        )

    def list(self, request, *args, **kwargs):
        if not request.query_params:
            cache_key = f"territory:precincts:{self.kwargs['pk']}"
            cached = cache.get(cache_key)
            if cached is not None:
                return Response(cached)
            response = super().list(request, *args, **kwargs)
            cache.set(cache_key, response.data, CACHE_TTL_TERRITORY)
            return response
        return super().list(request, *args, **kwargs)


@extend_schema(tags=["Territories"], summary="Get precinct detail")
class PrecinctDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single precinct by ID.

    Returns precinct with full hierarchy (district and region).
    """

    queryset = Precinct.objects.select_related("district__region")
    serializer_class = PrecinctSerializer
    permission_classes = [IsAuthenticated]


@extend_schema(
    tags=["Territories"],
    summary="Find nearby precincts by GPS coordinates",
    parameters=[
        OpenApiParameter("lat", float, required=True, description="Latitude (-90 to 90)"),
        OpenApiParameter("lng", float, required=True, description="Longitude (-180 to 180)"),
        OpenApiParameter("radius", float, description="Search radius in km (1-50, default 10)"),
    ],
)
class NearbyPrecinctsView(APIView):
    """
    Find precincts near given coordinates.

    Query parameters:
    - lat (required): Latitude (-90 to 90)
    - lng (required): Longitude (-180 to 180)
    - radius (optional): Search radius in km (1-50, default 10)

    Returns precincts within the specified radius, ordered by distance.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 1. Validate query params
        lat = request.GET.get("lat")
        lng = request.GET.get("lng")
        radius = request.GET.get("radius", 10)

        if not lat or not lng:
            return Response(
                {"detail": "Both 'lat' and 'lng' query parameters are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            lat = float(lat)
            lng = float(lng)
            radius = float(radius)
        except ValueError:
            return Response(
                {"detail": "Invalid coordinate values. Must be numeric."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            return Response(
                {"detail": "Coordinates out of range. Latitude: -90 to 90, Longitude: -180 to 180."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not (1 <= radius <= 50):
            return Response(
                {"detail": "Radius must be between 1 and 50 km."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 2. Get all precincts with coordinates
        precincts = Precinct.objects.filter(
            latitude__isnull=False, longitude__isnull=False
        ).select_related("district__region")

        # 3. Calculate distances and filter
        results = []
        for precinct in precincts:
            distance = haversine_distance(
                lat, lng, float(precinct.latitude), float(precinct.longitude)
            )
            if distance <= radius:
                results.append({"precinct": precinct, "distance": round(distance, 2)})

        # 4. Sort by distance
        results.sort(key=lambda x: x["distance"])

        # 5. Paginate
        paginator = StandardPagination()
        page = paginator.paginate_queryset([r["precinct"] for r in results], request)

        # 6. Serialize with distance
        serializer = PrecinctWithDistanceSerializer(page, many=True)
        serialized_data = serializer.data
        for i, result in enumerate(results[: len(page)]):
            serialized_data[i]["distance"] = result["distance"]

        return paginator.get_paginated_response(serialized_data)
