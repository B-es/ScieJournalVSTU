from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    """TS section 7: POST /api/auth/register body {fullName, email, password}."""

    fullName = serializers.CharField(source="full_name", max_length=255)
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["fullName", "email", "password"]

    def validate_email(self, value):
        email = value.lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Пользователь с таким email уже зарегистрирован.")
        return email

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get("request"),
            email=attrs["email"],
            password=attrs["password"],
        )
        if user is None:
            raise serializers.ValidationError("Неверный email или пароль.")
        if not user.is_active:
            raise serializers.ValidationError("Аккаунт деактивирован.")
        attrs["user"] = user
        return attrs


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class UserSerializer(serializers.ModelSerializer):
    roles = serializers.SlugRelatedField(slug_field="code", many=True, read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "full_name", "affiliation", "orcid", "language_pref", "roles"]


class ReviewerCandidateSerializer(serializers.ModelSerializer):
    """GET /api/users/reviewers — picker source for the chief editor's reviewer-assignment form (M3c plan decision #5)."""

    fullName = serializers.CharField(source="full_name")

    class Meta:
        model = User
        fields = ["id", "fullName", "email"]
