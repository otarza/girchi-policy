from rest_framework.routers import DefaultRouter

from . import views

app_name = "governance"

router = DefaultRouter()
router.register(r"elections", views.ElectionViewSet, basename="election")

urlpatterns = router.urls
