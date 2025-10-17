"""
User Application Configuration
==============================
Standard: IEEE 830
Requirements: RF-05

Django app configuration for users module.
"""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    Users application configuration.
    
    Requirement: RF-05 - User management module
    
    Design Thinking:
        - Prototype: Modular architecture for scalability
    """
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    verbose_name = 'User Management'
    
    def ready(self):
        """
        Import signals when app is ready.
        
        Purpose: Register signal handlers for user events
        """
        pass  # Import signals here if needed
