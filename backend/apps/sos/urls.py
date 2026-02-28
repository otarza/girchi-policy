from rest_framework.routers import DefaultRouter

from .views import SOSReportViewSet

router = DefaultRouter()
router.register("reports", SOSReportViewSet, basename="sos-report")

urlpatterns = router.urls
