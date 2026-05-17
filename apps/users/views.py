from rest_framework import generics, status, permissions
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from drf_spectacular.utils import extend_schema, inline_serializer
from .models import User
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    UserUpdateSerializer
)


# OopCompanion:suppressRename


def get_jwt_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class UserRegistrationView(generics.CreateAPIView):
    """View for registering a new user.
    
    Available without authentication. Returns the created user and JWT tokens.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            'user': UserProfileSerializer(user).data,
            'tokens': get_jwt_tokens(user),
        }, status=status.HTTP_201_CREATED)


@extend_schema(
    request=UserLoginSerializer,
    responses=inline_serializer(
        name='LoginResponse',
        fields={
            'user': UserProfileSerializer(),
            'tokens': serializers.DictField(),
        },
    )
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']

    return Response({
        'user': UserProfileSerializer(user).data,
        'tokens': get_jwt_tokens(user),
    })


@extend_schema(
    request=inline_serializer(
        name='LogoutRequest',
        fields={'refresh': serializers.CharField()},
    ),
    responses=inline_serializer(
        name='MessageResponse',
        fields={'message': serializers.CharField()},
    )
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'error': 'Refresh token обязателен'}, status=status.HTTP_400_BAD_REQUEST)

        RefreshToken(refresh_token).blacklist()
        return Response({'message': 'Вы успешно вышли из системы'})
    except Exception:
        return Response({'message': 'Ошибка при выходе'}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """View for viewing and updating user profile.
    
    Requires authentication. Uses different serializers for reading and updating.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Returns the current authenticated user.

        """
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserProfileSerializer


@extend_schema(responses=UserProfileSerializer)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def current_user_view(request):
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)


@extend_schema(
    request=inline_serializer(
        name='ChangePasswordRequest',
        fields={
            'old_password': serializers.CharField(),
            'new_password': serializers.CharField(),
        },
    ),
    responses=inline_serializer(
        name='ChangePasswordResponse',
        fields={'message': serializers.CharField()},
    )
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password_view(request):
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')

    if not old_password or not new_password:
        return Response(
            {'error': 'Старый и новый пароли обязательны'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not user.check_password(old_password):
        return Response(
            {'error': 'Неверный старый пароль'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if len(new_password) < 8:
        return Response(
            {'error': 'Новый пароль должен содержать минимум 8 символов'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user.set_password(new_password)
    user.save()

    for token in OutstandingToken.objects.filter(user=user):
        BlacklistedToken.objects.get_or_create(token=token)

    return Response({'message': 'Пароль успешно изменен'})
