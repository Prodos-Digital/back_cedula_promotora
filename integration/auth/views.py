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
from rolepermissions.roles import assign_role, get_user_roles
from rolepermissions.permissions import grant_permission, revoke_permission
from rest_framework.decorators import action
from django.db import transaction
from integration.users.serializers import UserSerializer

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
        try:
            data = request.data

            if User.objects.filter(email=data['email']).exists():
                return Response(status=status.HTTP_403_FORBIDDEN)
            
            data["password"] = '12345678'            
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            # Generate JWT tokens
            # refresh = RefreshToken.for_user(user)
            # token_data = {
            #     "refresh": str(refresh),
            #     "token": str(refresh.access_token),
            # }
        
            assign_role(user, 'app_permissions')
            assign_role(user, 'menu_permissions')            
            roles = get_user_roles(user)
            permissions = {perm: False for role in roles for perm in role.available_permissions}
         
            user_data = serializer.data
            #user_data.update(token_data)
            user_data['permissions'] = permissions

            return Response(user_data, status=status.HTTP_201_CREATED)

        except Exception as err:
            print("Error: ", err)
            return Response(data={'success': False, 'message': str(err)}, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['post'], url_path='update-perms')
    def change_permissions(self, request):      

        data = request.data
        user_id = data.get('user_id')
        permissions = data.get('permissions')
        is_active = data.get('is_active')

        if not data:
             return Response({'success': False, 'message': 'User ID and permissions are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                user = User.objects.get(id=user_id)

                if is_active is not None:
                    user.is_active = is_active
                    user.save()                  

                user_serializer = UserSerializer(user)

                if user:
                    for perm, value in permissions.items():
                        if value:
                            grant_permission(user, perm)
                        else:
                            revoke_permission(user, perm)
                
                return Response(user_serializer.data, status=status.HTTP_200_OK)

        except Exception as err:
            print("Error: ", err)
            return Response(data={'success': False, 'message': str(err)}, status=status.HTTP_400_BAD_REQUEST)