"""
User Admin Configuration
========================
Standard: IEEE 830
Requirements: RF-05, RF-06

Django admin interface for user management.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User Admin Interface.
    
    Requirements:
        - RF-05: User management by administrators
        - RF-06: Administrative dashboard
    
    Design Thinking:
        - Ideare: Intuitive admin interface
        - Evaluate: Quick access to user information
    """
    
    list_display = [
        'username',
        'email',
        'role',
        'first_name',
        'last_name',
        'is_active',
        'created_at'
    ]
    
    list_filter = [
        'role',
        'is_active',
        'is_staff',
        'created_at'
    ]
    
    search_fields = [
        'username',
        'email',
        'first_name',
        'last_name',
        'phone_number'
    ]
    
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        (_('Personal Info'), {
            'fields': ('first_name', 'last_name', 'email', 'phone_number')
        }),
        (_('Role & Permissions (RF-05)'), {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Important Dates'), {
            'fields': ('last_login', 'created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_login']
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'password1',
                'password2',
                'role',
                'is_staff',
                'is_active'
            ),
        }),
    )
