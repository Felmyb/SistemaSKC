"""
Orders Application Configuration
================================
Standard: IEEE 830
Requirements: RF-01, RF-04

Django app configuration for orders module.
"""

from django.apps import AppConfig


class OrdersConfig(AppConfig):
    """
    Orders application configuration.
    
    Requirements:
        - RF-01: Digital order panel
        - RF-04: Order tracking
    
    Design Thinking:
        - Empathize: Kitchen staff need clear order visibility
        - Prototype: Modular order management system
    """
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.orders'
    verbose_name = 'Order Management'
    
    def ready(self):
        """Import signals when app is ready."""
        try:
            import apps.orders.signals  # noqa
        except ImportError:
            pass
