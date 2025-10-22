import pytest
from django.contrib.auth import get_user_model
from apps.usuarios.models import UserRole

User = get_user_model()


@pytest.mark.django_db
def test_user_model_role_helpers():
    u = User.objects.create_user(username='x', password='p', role=UserRole.COOK)
    assert u.has_role(UserRole.COOK) is True
    assert u.has_role(UserRole.ADMINISTRATOR) is False
    assert u.is_staff_member() is True

    c = User.objects.create_user(username='y', password='p', role=UserRole.CUSTOMER)
    assert c.is_staff_member() is False
