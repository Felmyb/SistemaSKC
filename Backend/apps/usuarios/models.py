"""
Modelos de Usuario
==================
Estándar: IEEE 830
Requisitos: RF-05, RNF-03

Modelo de usuario y gestión de roles para SmartKitchen Connect.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserRole(models.TextChoices):
    """Enumeración de roles de usuario."""
    CUSTOMER = 'CUSTOMER', _('Cliente')
    COOK = 'COOK', _('Cocinero')
    INVENTORY_MANAGER = 'INVENTORY_MANAGER', _('Gestor de Inventario')
    ADMINISTRATOR = 'ADMINISTRATOR', _('Administrador')
    WAITER = 'WAITER', _('Mesero/Cajero')


class User(AbstractUser):
    """Modelo de Usuario personalizado."""

    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.CUSTOMER,
        help_text=_("Rol del usuario en el sistema (RF-05)")
    )

    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text=_("Teléfono de contacto para notificaciones (RF-04)")
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("Fecha de creación de la cuenta (trazabilidad)")
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("Última actualización (trazabilidad)")
    )

    class Meta:
        db_table = 'users'
        verbose_name = _('Usuario')
        verbose_name_plural = _('Usuarios')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    def has_role(self, role):
        return self.role == role

    def is_staff_member(self):
        return self.role in [
            UserRole.COOK,
            UserRole.INVENTORY_MANAGER,
            UserRole.ADMINISTRATOR,
            UserRole.WAITER
        ]
