import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


@pytest.mark.django_db
def test_me_returns_profile():
    user = User.objects.create_user(username='meuser', password='pass', role='CUSTOMER', email='me@ex.com')
    client = APIClient()
    client.force_authenticate(user=user)
    resp = client.get('/api/auth/users/me/')
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data['username'] == 'meuser'


@pytest.mark.django_db
def test_update_profile_success():
    user = User.objects.create_user(username='upd', password='pass', role='CUSTOMER', email='old@ex.com')
    client = APIClient()
    client.force_authenticate(user=user)
    payload = {"first_name": "Nuevo", "last_name": "Nombre", "email": "new@ex.com"}
    resp = client.patch('/api/auth/users/me/update/', payload, format='json')
    assert resp.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.first_name == 'Nuevo'
    assert user.email == 'new@ex.com'


@pytest.mark.django_db
def test_admin_can_list_users_and_customer_cannot():
    admin = User.objects.create_user(username='admin', password='pass', role='ADMINISTRATOR', is_staff=True)
    cust = User.objects.create_user(username='cust', password='pass', role='CUSTOMER')

    client = APIClient()

    # Customer cannot list
    client.force_authenticate(user=cust)
    resp_forbidden = client.get('/api/auth/users/')
    assert resp_forbidden.status_code in (status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED)

    # Admin can list
    client.force_authenticate(user=admin)
    resp_ok = client.get('/api/auth/users/')
    assert resp_ok.status_code == status.HTTP_200_OK
