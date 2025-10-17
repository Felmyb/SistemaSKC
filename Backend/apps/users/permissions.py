"""
User Permissions
================
Standard: IEEE 830
Requirements: RF-05, RNF-03

Custom permission classes for role-based access control.
"""

from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission: User can only access their own data, or admin can access all.
    
    Requirements:
        - RF-05: Role-based access control
        - RNF-03: Security through authorization
    
    Design Thinking:
        - Define: Clear separation between user roles
        - Evaluate: Protect user privacy while allowing admin oversight
    """
    
    message = "You don't have permission to access this resource."
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user owns the object or is admin.
        
        Args:
            request: HTTP request
            view: Current view
            obj: Object being accessed
        
        Returns:
            bool: True if permission granted
        
        Requirement: RF-05 - Permission verification
        """
        # Admins can access everything
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # Users can access their own data
        return obj == request.user


class IsAdminUser(permissions.BasePermission):
    """
    Permission: Only administrators can access.
    
    Requirements:
        - RF-05: Administrator-only actions
        - RNF-03: Secure administrative functions
    
    Design Thinking:
        - Define: Protect sensitive operations
    """
    
    message = "Administrator privileges required."
    
    def has_permission(self, request, view):
        """
        Check if user is administrator.
        
        Requirement: RF-05 - Admin verification
        """
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'ADMINISTRATOR'
        )


class IsCookUser(permissions.BasePermission):
    """
    Permission: Only cooks can access.
    
    Requirements:
        - RF-05: Cook-specific operations
        - RF-01: Kitchen panel access
    
    Design Thinking:
        - Empathize: Cooks need access to order management
        - Define: Restrict kitchen operations to authorized personnel
    """
    
    message = "Cook privileges required."
    
    def has_permission(self, request, view):
        """
        Check if user is a cook.
        
        Requirement: RF-05, RF-01
        """
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'COOK'
        )


class IsInventoryManager(permissions.BasePermission):
    """
    Permission: Only inventory managers can access.
    
    Requirements:
        - RF-05: Inventory manager operations
        - RF-02: Inventory management access
    
    Design Thinking:
        - Define: Secure inventory control
        - Evaluate: Prevent unauthorized inventory changes
    """
    
    message = "Inventory Manager privileges required."
    
    def has_permission(self, request, view):
        """
        Check if user is inventory manager.
        
        Requirement: RF-05, RF-02
        """
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'INVENTORY_MANAGER'
        )


class IsWaiterUser(permissions.BasePermission):
    """
    Permission: Only waiters can access.
    
    Requirements:
        - RF-05: Waiter operations
        - RF-01: Order creation access
    
    Design Thinking:
        - Empathize: Waiters are frontline users
        - Ideare: Streamlined order placement
    """
    
    message = "Waiter privileges required."
    
    def has_permission(self, request, view):
        """
        Check if user is a waiter.
        
        Requirement: RF-05
        """
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'WAITER'
        )
