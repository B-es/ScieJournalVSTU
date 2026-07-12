from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Role
from .serializers import LoginSerializer, PasswordResetSerializer, RegisterSerializer, UserSerializer


def _tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}


class RegisterView(APIView):
    """POST /api/auth/register — TS section 7. Default role: author (TS section 7 note)."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        author_role, _ = Role.objects.get_or_create(code=Role.AUTHOR)
        user.roles.add(author_role)

        return Response(
            {"userId": str(user.id), "token": _tokens_for_user(user)},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """POST /api/auth/login — TS section 7."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        roles = list(user.roles.values_list("code", flat=True))
        return Response({"token": _tokens_for_user(user), "roles": roles})


class LogoutView(APIView):
    """POST /api/auth/logout — blacklists the given refresh token."""

    def post(self, request):
        refresh = request.data.get("refresh")
        if not refresh:
            raise ValidationError({"refresh": "Обязательное поле."})
        try:
            RefreshToken(refresh).blacklist()
        except TokenError as exc:
            raise ValidationError({"refresh": str(exc)}) from exc
        return Response({"status": "ok"})


class PasswordResetView(APIView):
    """
    POST /api/auth/password-reset — TS section 7.
    Stub: validates the email shape and always returns 200 without leaking
    account existence. Actual email dispatch is implemented with the
    notifications module (see plan milestone M3+).
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"status": "ok"})


class MeView(APIView):
    """GET /api/auth/me — current authenticated user, used by the frontend authStore."""

    def get(self, request):
        return Response(UserSerializer(request.user).data)
