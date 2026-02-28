from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "governance"

router = DefaultRouter()
router.register(r"elections", views.ElectionViewSet, basename="election")
router.register(r"positions", views.LeaderPositionViewSet, basename="position")

urlpatterns = [
    path("hierarchy/", views.HierarchyTreeView.as_view(), name="hierarchy"),
] + router.urls
