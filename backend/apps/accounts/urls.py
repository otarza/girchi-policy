from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", views.ProfileView.as_view(), name="profile"),
    path("me/onboarding/", views.OnboardingView.as_view(), name="onboarding"),
    # Notifications
    path("notifications/", views.NotificationListView.as_view(), name="notifications"),
    path("notifications/mark-all-read/", views.NotificationMarkAllReadView.as_view(), name="notifications-mark-all-read"),
    path("notifications/<int:pk>/read/", views.NotificationMarkReadView.as_view(), name="notification-read"),
]
