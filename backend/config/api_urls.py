from django.urls import include, path

urlpatterns = [
    path("auth/", include("apps.accounts.urls")),
    path("verification/", include("apps.verification.urls")),
]
