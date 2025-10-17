"""
User Tests
==========
Standard: IEEE 830
Requirements: RNF-02 (80% test coverage)
Test Categories: Unit, Integration, Security

Purpose: Validate user management functionality and security.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """
    Test User Model.
    
    Requirement: RF-05 - User role management
    Design Thinking: Validate - Ensure model behaves correctly
    """
    
    def test_create_user(self):
        """Test basic user creation."""
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
    
    def test_user_role_display(self):
        """Test role display method (RF-05)."""
        user = User.objects.create_user(
            username='cook',
            password='pass',
            role='COOK'
        )
        assert user.get_role_display() == 'Cook'
    
    def test_is_staff_member(self):
        """Test staff member identification (RF-05)."""
        customer = User.objects.create_user(
            username='customer',
            password='pass',
            role='CUSTOMER'
        )
        cook = User.objects.create_user(
            username='cook',
            password='pass',
            role='COOK'
        )
        assert not customer.is_staff_member()
        assert cook.is_staff_member()


@pytest.mark.django_db
class TestUserRegistration:
    """
    Test User Registration Endpoint.
    
    Requirements:
        - RF-05: User registration
        - RNF-03: Secure authentication
    
    Design Thinking: Evaluate - User-friendly registration process
    """
    
    def setup_method(self):
        """Setup test client."""
        self.client = APIClient()
    
    def test_register_user_success(self):
        """Test successful user registration (RF-05)."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'CUSTOMER'
        }
        response = self.client.post('/api/users/register/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'user' in response.data
        assert 'tokens' in response.data
        assert response.data['user']['username'] == 'newuser'
    
    def test_register_password_mismatch(self):
        """Test registration with mismatched passwords (RNF-03)."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'DifferentPass123!',
            'role': 'CUSTOMER'
        }
        response = self.client.post('/api/users/register/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data


@pytest.mark.django_db
@pytest.mark.security
class TestUserPermissions:
    """
    Test User Permissions.
    
    Requirements:
        - RF-05: Role-based permissions
        - RNF-03: Security
    
    Design Thinking: Evaluate - Secure access control
    """
    
    def setup_method(self):
        """Setup test users and client."""
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username='admin',
            password='admin123',
            role='ADMINISTRATOR'
        )
        self.customer = User.objects.create_user(
            username='customer',
            password='cust123',
            role='CUSTOMER'
        )
    
    def test_customer_cannot_access_admin_endpoint(self):
        """Test customer permission restriction (RF-05, RNF-03)."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get('/api/users/')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_admin_can_access_user_list(self):
        """Test admin permission (RF-05)."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/users/')
        
        assert response.status_code == status.HTTP_200_OK
