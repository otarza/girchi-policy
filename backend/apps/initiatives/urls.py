from rest_framework.routers import DefaultRouter

from .views import InitiativeViewSet

router = DefaultRouter()
router.register("", InitiativeViewSet, basename="initiative")

urlpatterns = router.urls
