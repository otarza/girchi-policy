from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "communities"

router = DefaultRouter()
router.register(r"groups", views.GroupOfTenViewSet, basename="group")

urlpatterns = router.urls
