"""
Permisos de Usuarios
====================
Clases de permisos para control de acceso basado en roles.
"""

from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    message = "No tienes permisos para acceder a este recurso."

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True
        return obj == request.user


class IsAdminUser(permissions.BasePermission):
    message = "Se requieren privilegios de Administrador."

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'ADMINISTRATOR'
        )


class IsCookUser(permissions.BasePermission):
    message = "Se requieren privilegios de Cocinero."

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'COOK'
        )


class IsInventoryManager(permissions.BasePermission):
    message = "Se requieren privilegios de Gestor de Inventario."

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'INVENTORY_MANAGER'
        )


class IsWaiterUser(permissions.BasePermission):
    message = "Se requieren privilegios de Mesero."

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'WAITER'
        )
