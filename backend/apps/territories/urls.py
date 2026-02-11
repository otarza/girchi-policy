from django.urls import path

from . import views

app_name = "territories"

urlpatterns = [
    # Regions
    path("regions/", views.RegionListView.as_view(), name="region-list"),
    path(
        "regions/<int:pk>/districts/",
        views.RegionDistrictsView.as_view(),
        name="region-districts",
    ),
    # Districts
    path(
        "districts/<int:pk>/precincts/",
        views.DistrictPrecinctsView.as_view(),
        name="district-precincts",
    ),
    # Precincts
    path(
        "precincts/<int:pk>/",
        views.PrecinctDetailView.as_view(),
        name="precinct-detail",
    ),
    path("precincts/nearby/", views.NearbyPrecinctsView.as_view(), name="precinct-nearby"),
]
