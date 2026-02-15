from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers

from apps.territories.models import Precinct
from apps.territories.serializers import PrecinctSerializer

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = [
            "phone_number",
            "personal_id_number",
            "password",
            "first_name",
            "last_name",
        ]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    precinct = PrecinctSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "phone_number",
            "personal_id_number",
            "first_name",
            "last_name",
            "role",
            "member_status",
            "is_diaspora",
            "precinct",
            "is_phone_verified",
            "onboarding_completed",
            "constitution_accepted",
            "join_reason",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "phone_number",
            "personal_id_number",
            "role",
            "is_phone_verified",
            "onboarding_completed",
            "constitution_accepted",
            "created_at",
        ]


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    precinct_id = serializers.PrimaryKeyRelatedField(
        queryset=Precinct.objects.all(),
        source="precinct",
        required=False,
        allow_null=True,
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "member_status",
            "is_diaspora",
            "precinct_id",
        ]


class OnboardingSerializer(serializers.Serializer):
    join_reason = serializers.CharField(required=True)
    member_status = serializers.ChoiceField(choices=User.MemberStatus.choices)
    constitution_accepted = serializers.BooleanField()

    def validate_constitution_accepted(self, value):
        if not value:
            raise serializers.ValidationError(
                "You must accept the constitution to proceed."
            )
        return value

    def save(self, user):
        user.join_reason = self.validated_data["join_reason"]
        user.member_status = self.validated_data["member_status"]
        user.constitution_accepted = True
        user.constitution_accepted_at = timezone.now()
        user.onboarding_completed = True
        # Django 6: keyword-only args for save()
        user.save(
            update_fields=[
                "join_reason",
                "member_status",
                "constitution_accepted",
                "constitution_accepted_at",
                "onboarding_completed",
            ]
        )
        return user
