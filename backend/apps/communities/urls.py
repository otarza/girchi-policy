from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "communities"

router = DefaultRouter()
router.register(r"groups", views.GroupOfTenViewSet, basename="group")
router.register(r"endorsements", views.EndorsementViewSet, basename="endorsement")

urlpatterns = [
    path("nearby-geders/", views.NearbyGeDersView.as_view(), name="nearby-geders"),
] + router.urls
