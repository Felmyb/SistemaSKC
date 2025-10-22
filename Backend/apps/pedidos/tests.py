import pytest
from decimal import Decimal
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.pedidos.models import Order, OrderItem, OrderPriority, OrderStatus
from apps.platos.models import Dish, DishCategory

User = get_user_model()


@pytest.mark.django_db
def test_order_and_order_item_behaviors():
    user = User.objects.create_user(username='c', password='p')
    dish = Dish.objects.create(name='Soup', description='Hot', category=DishCategory.SOUP, price=Decimal('7.50'))

    order = Order.objects.create(customer=user, priority=OrderPriority.HIGH, order_type='TAKEOUT')
    item = OrderItem.objects.create(order=order, dish=dish, quantity=2, unit_price=dish.price)

    # save should compute subtotal
    assert item.subtotal == Decimal('15.00')

    # calculate_total sums items and saves
    total = order.calculate_total()
    assert total == Decimal('15.00')
    order.refresh_from_db()
    assert order.total_amount == Decimal('15.00')

    # priority color mapping
    assert order.get_priority_color() in {'#4CAF50', '#FFC107', '#FF9800', '#F44336'}

    # __str__ contains username and status
    s = str(order)
    assert user.username in s and order.status in s


@pytest.mark.django_db
def test_signals_delivered_sets_completed_at():
    user = User.objects.create_user(username='d', password='p')
    dish = Dish.objects.create(name='Pizza', description='Cheese', price=Decimal('12.00'))
    order = Order.objects.create(customer=user, order_type='DINE_IN', table_number='5')
    OrderItem.objects.create(order=order, dish=dish, quantity=1, unit_price=dish.price)

    # Transition to DELIVERED triggers completed_at
    order.status = OrderStatus.DELIVERED
    order.save()
    order.refresh_from_db()
    assert order.completed_at is not None
