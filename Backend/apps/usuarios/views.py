"""
Vistas de Usuario
=================
Endpoints de API para gestión de usuarios y autenticación.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import User
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    UserProfileSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'register':
            return UserRegistrationSerializer
        elif self.action == 'update_profile':
            return UserProfileSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in ['register', 'create']:
            return [permissions.AllowAny()]
        elif self.action in ['me', 'update_profile']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

    @swagger_auto_schema(
        operation_summary="Registro de nuevo usuario",
        operation_description="Registro público de usuarios (RF-05)",
        request_body=UserRegistrationSerializer,
        responses={
            201: openapi.Response(description="Usuario creado", schema=UserSerializer),
            400: "Error de validación"
        },
        tags=['Autenticación']
    )
    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Usuario registrado correctamente'
        }, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary="Perfil del usuario actual",
        operation_description="Obtiene el perfil del usuario autenticado (RF-05)",
        responses={200: UserSerializer, 401: "No autorizado"},
        tags=['Perfil']
    )
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @swagger_auto_schema(
        methods=['put', 'patch'],
        operation_summary="Actualizar perfil",
        operation_description="Actualiza el perfil del usuario autenticado (RF-05)",
        request_body=UserProfileSerializer,
        responses={200: UserSerializer, 400: "Error de validación", 401: "No autorizado"},
        tags=['Perfil']
    )
    @action(detail=False, methods=['put', 'patch'], url_path='me/update')
    def update_profile(self, request):
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'user': UserSerializer(request.user).data, 'message': 'Perfil actualizado'})
