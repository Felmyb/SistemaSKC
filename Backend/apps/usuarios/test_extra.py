import pytest
from apps.usuarios.models import User, UserRole
from apps.usuarios.serializers import UserRegistrationSerializer


@pytest.mark.django_db
def test_user_role_helpers_and_registration_success():
    u = User.objects.create_user(username='w', password='p', role=UserRole.WAITER)
    assert u.has_role(UserRole.WAITER) is True
    assert u.has_role(UserRole.CUSTOMER) is False
    assert u.is_staff_member() is True

    # Registration successful path (validate returns attrs)
    data = {
        'username': 'newuser', 'email': 'n@x.com', 'password': 'Passw0rd!1', 'password_confirm': 'Passw0rd!1',
        'first_name': 'N', 'last_name': 'U', 'phone_number': '123456789'
    }
    ser = UserRegistrationSerializer(data=data)
    assert ser.is_valid(), ser.errors
    user = ser.save()
    assert user.username == 'newuser'


@pytest.mark.django_db
def test_user_str_and_registration_mismatch():
    u = User.objects.create_user(username='u2', password='p', role=UserRole.CUSTOMER)
    assert u.username in str(u)

    data = {
        'username': 'bad', 'email': 'b@x.com', 'password': 'Passw0rd!1', 'password_confirm': 'Mismatch!1',
        'first_name': 'B', 'last_name': 'X'
    }
    ser = UserRegistrationSerializer(data=data)
    assert ser.is_valid() is False
