"""
URLs para el módulo de Pedidos
===============================
RF-01, RF-04: Gestión y seguimiento de pedidos
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet

app_name = 'pedidos'

# Router para ViewSets
router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
]
