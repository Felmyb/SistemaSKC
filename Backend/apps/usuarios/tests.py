"""
Pruebas de Usuarios
===================
Cobertura básica de modelo y endpoints.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    def test_create_user(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!',
            role='CUSTOMER'
        )
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.role == 'CUSTOMER'
        assert user.check_password('TestPass123!')


@pytest.mark.django_db
class TestUserRegistration:
    def setup_method(self):
        self.client = APIClient()

    def test_register_user_success(self):
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'CUSTOMER'
        }
        response = self.client.post('/api/auth/users/register/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert 'user' in response.data
        assert 'tokens' in response.data
