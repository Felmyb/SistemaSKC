"""
Permisos personalizados para el módulo de Platos
=================================================
RNF-03: Control de acceso basado en roles
"""

from rest_framework import permissions


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado:
    - Lectura (GET, HEAD, OPTIONS): permitido para todos los usuarios autenticados
    - Escritura (POST, PUT, PATCH, DELETE): solo para staff y admin
    
    RF-01: Los clientes pueden ver el menú, pero solo el staff puede modificarlo.
    """
    
    def has_permission(self, request, view):
        # Lectura permitida para usuarios autenticados
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Escritura solo para staff/admin
        return request.user and request.user.is_authenticated and (
            request.user.role in ['STAFF', 'ADMIN'] or request.user.is_staff
        )
