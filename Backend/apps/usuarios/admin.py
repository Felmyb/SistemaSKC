"""
Configuración del Admin de Usuarios
===================================
Estándar: IEEE 830
Requisitos: RF-05, RF-06

Interfaz de administración de Django para gestión de usuarios.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin personalizado para Usuarios.
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
        (_('Información Personal'), {
            'fields': ('first_name', 'last_name', 'email', 'phone_number')
        }),
        (_('Rol y Permisos (RF-05)'), {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Fechas Importantes'), {
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
