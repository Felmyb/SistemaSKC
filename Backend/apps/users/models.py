"""
User Models
===========
Standard: IEEE 830
Requirements: RF-05, RNF-03

This module defines the user model and role management for SmartKitchen Connect.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserRole(models.TextChoices):
    """
    User role enumeration.
    
    Requirement: RF-05 - Differentiated user roles
    
    Design Thinking:
        - Empathize: Each role represents a real person with specific needs
        - Define: Clear separation of concerns and responsibilities
    """
    CUSTOMER = 'CUSTOMER', _('Customer')
    COOK = 'COOK', _('Cook')
    INVENTORY_MANAGER = 'INVENTORY_MANAGER', _('Inventory Manager')
    ADMINISTRATOR = 'ADMINISTRATOR', _('Administrator')
    WAITER = 'WAITER', _('Waiter/Cashier')


class User(AbstractUser):
    """
    Custom User Model.
    
    Requirements:
        - RF-05: Role-based access control
        - RNF-03: Secure authentication
        - RNF-06: Accessible user interface
    
    Design Thinking:
        - Empathize: Users need clear roles and easy authentication
        - Prototype: Flexible model that supports future extensions
    
    Attributes:
        role (str): User's role in the system
        phone_number (str): Contact phone number
        is_active (bool): Account status
        created_at (datetime): Account creation timestamp
        updated_at (datetime): Last update timestamp
    """
    
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.CUSTOMER,
        help_text=_("User's role in the system (RF-05)")
    )
    
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text=_("Contact phone number for notifications (RF-04)")
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("Account creation timestamp (traceability)")
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("Last update timestamp (traceability)")
    )
    
    class Meta:
        db_table = 'users'
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]
    
    def __str__(self):
        """String representation of user."""
        return f"{self.username} ({self.get_role_display()})"
    
    def has_role(self, role):
        """
        Check if user has specific role.
        
        Args:
            role (str): Role to check
        
        Returns:
            bool: True if user has the role
        
        Requirement: RF-05 - Role verification
        """
        return self.role == role
    
    def is_staff_member(self):
        """
        Check if user is a staff member (not a customer).
        
        Returns:
            bool: True if user is staff
        
        Design Thinking:
            - Define: Clear distinction between customers and staff
        """
        return self.role in [
            UserRole.COOK,
            UserRole.INVENTORY_MANAGER,
            UserRole.ADMINISTRATOR,
            UserRole.WAITER
        ]
