from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import IsPhoneVerified

from .models import Notification
from .serializers import (
    NotificationSerializer,
    OnboardingSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    UserRegistrationSerializer,
)


@extend_schema(tags=["Auth"], summary="Register a new user")
class RegisterView(generics.CreateAPIView):
    """Register a new user with phone number and personal ID."""

    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            UserProfileSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )


@extend_schema_view(
    get=extend_schema(tags=["Auth"], summary="Get my profile"),
    patch=extend_schema(tags=["Auth"], summary="Update my profile"),
)
class ProfileView(APIView):
    """Get or update authenticated user's profile."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserProfileUpdateSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserProfileSerializer(request.user).data)


@extend_schema(tags=["Auth"], summary="Complete onboarding")
class OnboardingView(APIView):
    """Complete the onboarding flow."""

    permission_classes = [IsAuthenticated, IsPhoneVerified]

    def post(self, request):
        if request.user.onboarding_completed:
            return Response(
                {"detail": "Onboarding already completed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = OnboardingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(user=request.user)
        return Response(UserProfileSerializer(user).data)


@extend_schema(
    tags=["Notifications"],
    summary="List my notifications",
    parameters=[OpenApiParameter("unread_only", bool, description="Return only unread notifications")],
)
class NotificationListView(generics.ListAPIView):
    """
    GET /api/v1/auth/notifications/

    Returns the authenticated user's notifications, newest first.
    Supports ?unread_only=true to filter unread notifications.
    """

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Notification.objects.filter(user=self.request.user)
        if self.request.query_params.get("unread_only") == "true":
            qs = qs.filter(is_read=False)
        return qs


@extend_schema(tags=["Notifications"], summary="Mark notification as read")
class NotificationMarkReadView(APIView):
    """
    PATCH /api/v1/auth/notifications/{id}/read/

    Mark a single notification as read.
    """

    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, user=request.user)
        except Notification.DoesNotExist:
            return Response(
                {"error": "NOT_FOUND", "message": "Notification not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        notification.is_read = True
        notification.save(update_fields=["is_read"])
        return Response(NotificationSerializer(notification).data)


@extend_schema(tags=["Notifications"], summary="Mark all notifications as read")
class NotificationMarkAllReadView(APIView):
    """
    POST /api/v1/auth/notifications/mark-all-read/

    Mark all unread notifications for the authenticated user as read.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        count = Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({"marked_read": count})
