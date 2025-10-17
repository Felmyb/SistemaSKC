"""
User Serializers
================
Standard: IEEE 830
Requirements: RF-05, RNF-03, RNF-04

Serializers for user data validation and transformation.
"""

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, UserRole


class UserSerializer(serializers.ModelSerializer):
    """
    User serializer for general operations.
    
    Requirements:
        - RF-05: Role-based data exposure
        - RNF-03: Password security
        - RNF-04: API documentation
    
    Design Thinking:
        - Evaluate: Ensure data security while maintaining usability
    """
    
    role_display = serializers.CharField(
        source='get_role_display',
        read_only=True,
        help_text="Human-readable role name"
    )
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
            'role_display',
            'phone_number',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    
    Requirements:
        - RNF-03: Secure password validation
        - RF-05: Role assignment
    
    Design Thinking:
        - Empathize: Easy registration process
        - Prototype: Validation ensures data quality
    """
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'},
        help_text="Password must meet security requirements (RNF-03)"
    )
    
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Confirm password"
    )
    
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'password_confirm',
            'first_name',
            'last_name',
            'phone_number',
            'role'
        ]
        extra_kwargs = {
            'role': {
                'default': UserRole.CUSTOMER,
                'help_text': "User role (RF-05)"
            }
        }
    
    def validate(self, attrs):
        """
        Validate password confirmation.
        
        Requirement: RNF-03 - Password security
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs
    
    def create(self, validated_data):
        """
        Create user with hashed password.
        
        Requirement: RNF-03 - Secure password storage
        """
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile updates.
    
    Requirements:
        - RF-05: User can update their own profile
        - RNF-06: Accessible profile management
    
    Design Thinking:
        - Ideare: Simple profile management
        - Evaluate: User-friendly field updates
    """
    
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone_number'
        ]
