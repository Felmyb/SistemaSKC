import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
from apps.usuarios.permissions import (
    IsOwnerOrAdmin,
    IsAdminUser,
    IsCookUser,
    IsInventoryManager,
    IsWaiterUser,
)

User = get_user_model()


@pytest.mark.django_db
def test_is_owner_or_admin_owner_object():
    user = User.objects.create_user(username='u', password='p', role='CUSTOMER')
    request = APIRequestFactory().get('/')
    request.user = user
    perm = IsOwnerOrAdmin()
    assert perm.has_object_permission(request, None, user) is True


@pytest.mark.django_db
def test_is_owner_or_admin_admin_access():
    admin = User.objects.create_user(username='a', password='p', role='ADMINISTRATOR', is_staff=True)
    other = User.objects.create_user(username='o', password='p', role='CUSTOMER')
    request = APIRequestFactory().get('/')
    request.user = admin
    perm = IsOwnerOrAdmin()
    assert perm.has_object_permission(request, None, other) is True


@pytest.mark.django_db
@pytest.mark.parametrize("role,cls,allowed", [
    ('ADMINISTRATOR', IsAdminUser, True),
    ('COOK', IsCookUser, True),
    ('INVENTORY_MANAGER', IsInventoryManager, True),
    ('WAITER', IsWaiterUser, True),
    ('CUSTOMER', IsAdminUser, False),
])
def test_role_permissions(role, cls, allowed):
    user = User.objects.create_user(username='u_'+role, password='p', role=role)
    request = APIRequestFactory().get('/')
    request.user = user
    perm = cls()
    assert perm.has_permission(request, None) is allowed
