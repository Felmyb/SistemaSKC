"""
URLs para el módulo de Platos
==============================
RF-01: Gestión del menú digital
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DishViewSet

app_name = 'platos'

# Router para ViewSets
router = DefaultRouter()
router.register(r'dishes', DishViewSet, basename='dish')

urlpatterns = [
    path('', include(router.urls)),
]
