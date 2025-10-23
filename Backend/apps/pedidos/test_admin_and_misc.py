import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.usuarios.models import User
from apps.platos.models import Dish, DishCategory
from apps.pedidos.models import Order, OrderItem, OrderPriority, OrderStatus
from apps.pedidos.admin import OrderAdmin
from django.apps import apps as django_apps
from apps.pedidos.permissions import IsOwnerOrStaff, IsStaffOrReadOnlyOwn, IsStaffOnly
from apps.pedidos.signals import update_dish_popularity


@pytest.fixture
def rf():
    return RequestFactory()


@pytest.fixture
def admin_user():
    return User.objects.create_user(username='adminuser', password='p', role='ADMIN')


@pytest.fixture
def staff_user():
    return User.objects.create_user(username='staffuser', password='p', role='STAFF')


@pytest.fixture
def customer_user():
    return User.objects.create_user(username='custuser', password='p', role='CUSTOMER')


@pytest.fixture
def dish():
    return Dish.objects.create(
        name='Soup', description='Hot soup', category=DishCategory.SOUP, price=5
    )


@pytest.mark.django_db
def test_admin_colored_fields_and_actions(rf, admin_user, customer_user, dish):
    site = AdminSite()
    order = Order.objects.create(customer=customer_user, status=OrderStatus.PENDING)
    OrderItem.objects.create(order=order, dish=dish, quantity=1, unit_price=dish.price)
    admin = OrderAdmin(Order, site)

    # Colored fields
    assert 'span' in admin.status_colored(order)
    assert 'span' in admin.priority_colored(order)

    # Actions change status
    req = rf.post('/')
    req.user = admin_user
    # Enable session and messages framework for admin.message_user
    SessionMiddleware(lambda r: None).process_request(req)
    req.session.save()
    setattr(req, '_messages', FallbackStorage(req))
    admin.mark_as_confirmed(req, Order.objects.filter(id=order.id))
    order.refresh_from_db(); assert order.status == OrderStatus.CONFIRMED
    admin.mark_as_in_progress(req, Order.objects.filter(id=order.id))
    order.refresh_from_db(); assert order.status == OrderStatus.IN_PROGRESS
    admin.mark_as_ready(req, Order.objects.filter(id=order.id))
    order.refresh_from_db(); assert order.status == OrderStatus.READY


@pytest.mark.django_db
def test_ready_method_safe_to_call():
    # Ensure ready() does not raise when called on the real AppConfig
    cfg = django_apps.get_app_config('pedidos')
    cfg.ready()


@pytest.mark.django_db
def test_permissions_negative_branches(rf, customer_user, staff_user):
    # IsOwnerOrStaff denies others
    perm1 = IsOwnerOrStaff()
    req = rf.get('/')
    req.user = customer_user
    class Obj: pass
    o = Obj(); o.customer = staff_user
    assert perm1.has_object_permission(req, None, o) is False

    # IsStaffOrReadOnlyOwn denies PATCH for customer
    perm2 = IsStaffOrReadOnlyOwn()
    req2 = rf.patch('/')
    req2.user = customer_user
    assert perm2.has_permission(req2, None) is False

    # IsStaffOnly denies non-staff
    perm3 = IsStaffOnly()
    req3 = rf.get('/')
    req3.user = customer_user
    assert perm3.has_permission(req3, None) is False

    # Positive staff/object branches
    req_staff_get = rf.get('/')
    req_staff_get.user = staff_user
    assert perm2.has_permission(req_staff_get, None) is True

    obj = type('Obj', (), {'customer': customer_user})()
    assert perm1.has_object_permission(req_staff_get, None, obj) is True
    # IsStaffOrReadOnlyOwn object GET for owner returns True
    req_get_own = rf.get('/')
    req_get_own.user = customer_user
    # First as non-owner -> False
    obj.customer = staff_user
    assert IsStaffOrReadOnlyOwn().has_object_permission(req_get_own, None, obj) is False
    # Then owner -> True
    obj.customer = customer_user
    assert IsStaffOrReadOnlyOwn().has_object_permission(req_get_own, None, obj) is True

    # IsStaffOnly allows staff
    assert IsStaffOnly().has_permission(req_staff_get, None) is True


@pytest.mark.django_db
def test_signals_update_dish_popularity(customer_user, dish):
    order = Order.objects.create(customer=customer_user, status=OrderStatus.PENDING)
    OrderItem.objects.create(order=order, dish=dish, quantity=1, unit_price=dish.price)
    # Manually invoke to cover loop body
    update_dish_popularity(Order, order, created=True)
    dish.refresh_from_db(); assert dish.popularity_score >= 1


@pytest.mark.django_db
def test_order_custom_actions_params(staff_user, customer_user, dish):
    api = APIClient(); api.force_authenticate(user=staff_user)
    # Create some orders with differing priorities and statuses
    for pr in [OrderPriority.LOW, OrderPriority.HIGH]:
        Order.objects.create(customer=customer_user, status=OrderStatus.PENDING, priority=pr)

    # active with priority filter
    url_active = reverse('pedidos:order-active')
    r1 = api.get(url_active, {'priority': OrderPriority.HIGH})
    assert r1.status_code == status.HTTP_200_OK

    # history with limit (and invalid limit)
    Order.objects.create(customer=customer_user, status=OrderStatus.DELIVERED)
    url_hist = reverse('pedidos:order-history')
    r2 = api.get(url_hist, {'limit': 1}); assert r2.status_code == status.HTTP_200_OK
    r3 = api.get(url_hist, {'limit': 'bad'}); assert r3.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_orderitem_str(customer_user, dish):
    order = Order.objects.create(customer=customer_user)
    item = OrderItem.objects.create(order=order, dish=dish, quantity=2, unit_price=dish.price)
    assert '2×' in str(item)
