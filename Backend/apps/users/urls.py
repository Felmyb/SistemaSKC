"""
User URL Configuration
======================
Standard: IEEE 830
Requirements: RF-05, RNF-04

URL routing for user management endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet

# Requirement: RNF-04 - RESTful API structure
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

app_name = 'users'

urlpatterns = [
    path('', include(router.urls)),
]
