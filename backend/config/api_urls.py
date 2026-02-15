from django.urls import include, path

urlpatterns = [
    path("auth/", include("apps.accounts.urls")),
    path("verification/", include("apps.verification.urls")),
    path("territories/", include("apps.territories.urls")),
    path("communities/", include("apps.communities.urls")),
]
