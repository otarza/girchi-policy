from django.urls import path

from .views import (
    CapabilitiesView,
    MyProgressView,
    PrecinctProgressView,
    UnlockedCapabilitiesView,
)

urlpatterns = [
    path("progress/", MyProgressView.as_view(), name="gamification-my-progress"),
    path("progress/<int:precinct_id>/", PrecinctProgressView.as_view(), name="gamification-precinct-progress"),
    path("capabilities/", CapabilitiesView.as_view(), name="gamification-capabilities"),
    path("capabilities/unlocked/", UnlockedCapabilitiesView.as_view(), name="gamification-unlocked"),
]
