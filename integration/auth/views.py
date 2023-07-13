from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.settings import api_settings

from integration.auth.serializers import LoginSerializer, RegistrationSerializer
from integration.users.models import User

User = get_user_model()


class LoginViewSet(ModelViewSet, TokenObtainPairView):
    """
    Classe utilizada para receber requisições de login dos usuários.
    """

    serializer_class = LoginSerializer
    permission_classes = (AllowAny,)
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        user = serializer.validated_data['user']
        model_user = User.objects.get(email=user['email'])
        user['token'] = serializer.validated_data['access']
        user['refresh'] = serializer.validated_data['refresh']

        return Response(user, status=status.HTTP_200_OK)


class RegistrationViewSet(ModelViewSet, TokenObtainPairView):
    """
    Classe utilizada para receber requisições de registro dos usuários.
    """

    serializer_class = RegistrationSerializer
    permission_classes = (AllowAny,)
    http_method_names = ['post']

    def create(self, request, nr_matricula=None, session_time=None, *args, **kwargs):

        data = request.data

        if User.objects.filter(email=data['email']).exists():
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=data)

        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)

        user = {
            "refresh": str(refresh),
            "token": str(refresh.access_token),
        }
        user.update(serializer.data)

        return Response(user, status=status.HTTP_201_CREATED)
