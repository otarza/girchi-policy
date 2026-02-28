from rest_framework.routers import DefaultRouter

from .views import ArbitrationCaseViewSet

router = DefaultRouter()
router.register("cases", ArbitrationCaseViewSet, basename="arbitration-case")

urlpatterns = router.urls
