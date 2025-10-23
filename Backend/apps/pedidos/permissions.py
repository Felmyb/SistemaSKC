"""
Permisos personalizados para el módulo de Pedidos
==================================================
RNF-03: Control de acceso basado en roles
RF-04: Los clientes solo ven sus propios pedidos, el staff ve todos
"""

from rest_framework import permissions


class IsOwnerOrStaff(permissions.BasePermission):
    """
    Permiso personalizado:
    - Los clientes solo pueden ver/editar sus propios pedidos
    - Staff y admin pueden ver/editar todos los pedidos
    
    RF-04: Control de acceso a pedidos
    """
    
    def has_permission(self, request, view):
        # Solo usuarios autenticados pueden acceder
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Staff y admin tienen acceso completo
        if request.user.role in ['STAFF', 'ADMIN'] or request.user.is_staff:
            return True
        
        # Los clientes solo acceden a sus propios pedidos
        return obj.customer == request.user


class IsStaffOrReadOnlyOwn(permissions.BasePermission):
    """
    Permiso para acciones específicas:
    - Clientes pueden crear pedidos (para sí mismos)
    - Clientes pueden ver sus propios pedidos
    - Solo staff/admin pueden actualizar estados o ver pedidos de otros
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Staff y admin tienen acceso completo
        if request.user.role in ['STAFF', 'ADMIN'] or request.user.is_staff:
            return True
        
        # Clientes pueden crear (POST) y listar (GET) sus propios pedidos
        if request.method in ['GET', 'POST']:
            return True
        
        # PUT, PATCH, DELETE requieren staff
        return False
    
    def has_object_permission(self, request, view, obj):
        # Staff y admin tienen acceso completo
        if request.user.role in ['STAFF', 'ADMIN'] or request.user.is_staff:
            return True
        
        # Los clientes solo pueden ver (GET) sus propios pedidos
        if request.method == 'GET':
            return obj.customer == request.user
        
        # No pueden modificar pedidos (ni propios) - solo staff
        return False


class IsStaffOnly(permissions.BasePermission):
    """
    Permiso estricto solo para staff/admin.
    Para acciones críticas como actualizar estados.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (request.user.role in ['STAFF', 'ADMIN'] or request.user.is_staff)
        )
