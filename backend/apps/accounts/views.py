from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import IsPhoneVerified

from .serializers import (
    OnboardingSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    UserRegistrationSerializer,
)


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
