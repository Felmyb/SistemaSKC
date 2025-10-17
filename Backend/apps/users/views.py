"""
User Views
==========
Standard: IEEE 830
Requirements: RF-05, RNF-01, RNF-03

API endpoints for user management and authentication.
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
from .permissions import IsOwnerOrAdmin


class UserViewSet(viewsets.ModelViewSet):
    """
    User Management ViewSet.
    
    Requirements:
        - RF-05: User and role management
        - RNF-01: Performance < 2 seconds
        - RNF-03: JWT authentication
        - RNF-04: OpenAPI documentation
    
    Design Thinking:
        - Empathize: Users need intuitive API endpoints
        - Ideare: RESTful design for clarity
        - Evaluate: Performance monitoring per endpoint
    
    Endpoints:
        - GET /users/ - List all users (admin only)
        - POST /users/ - Register new user
        - GET /users/{id}/ - Retrieve user details
        - PUT /users/{id}/ - Update user
        - DELETE /users/{id}/ - Deactivate user
        - POST /users/register/ - Public registration
        - GET /users/me/ - Get current user profile
        - PUT /users/me/update/ - Update own profile
    """
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """
        Select serializer based on action.
        
        Requirement: RNF-04 - Clear API documentation
        """
        if self.action == 'register':
            return UserRegistrationSerializer
        elif self.action == 'update_profile':
            return UserProfileSerializer
        return UserSerializer
    
    def get_permissions(self):
        """
        Set permissions based on action.
        
        Requirement: RF-05 - Role-based permissions
        """
        if self.action in ['register', 'create']:
            return [permissions.AllowAny()]
        elif self.action in ['me', 'update_profile']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]
    
    @swagger_auto_schema(
        operation_summary="Register new user",
        operation_description="Public endpoint for user registration (RF-05)",
        request_body=UserRegistrationSerializer,
        responses={
            201: openapi.Response(
                description="User created successfully",
                schema=UserSerializer
            ),
            400: "Validation error"
        },
        tags=['Authentication']
    )
    @action(detail=False, methods=['post'])
    def register(self, request):
        """
        Register a new user.
        
        Requirements:
            - RF-05: User registration
            - RNF-03: Secure password handling
        
        Design Thinking:
            - Empathize: Simple registration process
            - Evaluate: Clear error messages
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens (RNF-03)
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)
    
    @swagger_auto_schema(
        operation_summary="Get current user profile",
        operation_description="Retrieve authenticated user's profile (RF-05)",
        responses={
            200: UserSerializer,
            401: "Unauthorized"
        },
        tags=['User Profile']
    )
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Get current user's profile.
        
        Requirements:
            - RF-05: User profile access
            - RNF-01: Fast response time
        
        Design Thinking:
            - Evaluate: Users can easily view their information
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_summary="Update current user profile",
        operation_description="Update authenticated user's profile (RF-05)",
        request_body=UserProfileSerializer,
        responses={
            200: UserSerializer,
            400: "Validation error",
            401: "Unauthorized"
        },
        tags=['User Profile']
    )
    @action(detail=False, methods=['put', 'patch'], url_path='me/update')
    def update_profile(self, request):
        """
        Update current user's profile.
        
        Requirements:
            - RF-05: User profile management
            - RNF-06: User-friendly updates
        
        Design Thinking:
            - Ideare: Self-service profile management
            - Evaluate: Instant feedback on changes
        """
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'user': UserSerializer(request.user).data,
            'message': 'Profile updated successfully'
        })
