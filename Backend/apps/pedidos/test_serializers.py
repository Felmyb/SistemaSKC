import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework import serializers
from apps.pedidos.serializers import (
    OrderSerializer,
    OrderItemSerializer,
    OrderCreateSerializer,
    OrderStatusUpdateSerializer,
)
from apps.pedidos.models import Order, OrderStatus, OrderPriority
from apps.platos.models import Dish
from apps.inventario.models import Ingredient, InventoryStock, UnitOfMeasure

User = get_user_model()


@pytest.mark.django_db
def test_order_serializer_validate_table_number_required_for_dine_in():
    user = User.objects.create_user(username='u', password='p')
    data = {
        'customer': user.id,
        'order_type': 'DINE_IN',
        'priority': OrderPriority.MEDIUM,
        'estimated_time': 10,
    }
    ser = OrderSerializer(data=data)
    with pytest.raises(serializers.ValidationError):
        ser.is_valid(raise_exception=True)

    # TAKEOUT should pass without table_number
    data_takeout = {**data, 'order_type': 'TAKEOUT'}
    ser2 = OrderSerializer(data=data_takeout)
    assert ser2.is_valid() is True


@pytest.mark.django_db
def test_order_item_serializer_validates_dish_availability_and_stock():
    # Dish not available
    dish1 = Dish.objects.create(name='X', description='x', price=Decimal('5.00'), is_available=False)
    ser = OrderItemSerializer(data={'dish': dish1.id, 'quantity': 1, 'unit_price': '5.00'})
    with pytest.raises(serializers.ValidationError):
        ser.is_valid(raise_exception=True)

    # Dish available but ingredients insufficient
    ing = Ingredient.objects.create(name='Y', unit=UnitOfMeasure.GRAM, cost_per_unit=Decimal('1.00'))
    InventoryStock.objects.create(ingredient=ing, quantity=Decimal('0.50'))
    dish2 = Dish.objects.create(name='YDish', description='y', price=Decimal('8.00'), is_available=True)
    # Require more than in stock
    dish2.recipe_items.create(ingredient=ing, quantity=Decimal('1.00'))

    ser2 = OrderItemSerializer(data={'dish': dish2.id, 'quantity': 1, 'unit_price': '8.00'})
    with pytest.raises(serializers.ValidationError):
        ser2.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_order_create_serializer_creates_items_and_sets_totals():
    user = User.objects.create_user(username='u2', password='p')
    dish = Dish.objects.create(name='Burger', description='b', price=Decimal('9.50'), is_available=True)
    ser = OrderCreateSerializer(data={
        'customer': user.id,
        'order_type': 'TAKEOUT',
        'priority': OrderPriority.LOW,
        'estimated_time': 5,
        'items': [
            {'dish': dish.id, 'quantity': 2}
        ]
    })
    ser.is_valid(raise_exception=True)
    order = ser.save()
    assert order.items.count() == 1
    item = order.items.first()
    # unit_price must be overridden by serializer to dish.price
    assert item.unit_price == dish.price
    assert item.subtotal == dish.price * 2
    assert order.total_amount == item.subtotal


@pytest.mark.django_db
def test_order_status_update_serializer_validates_transitions():
    user = User.objects.create_user(username='u3', password='p')
    order = Order.objects.create(customer=user, status=OrderStatus.PENDING)

    ser = OrderStatusUpdateSerializer(data={'status': OrderStatus.CONFIRMED}, context={'order': order})
    ser.is_valid(raise_exception=True)

    ser_invalid = OrderStatusUpdateSerializer(data={'status': OrderStatus.READY}, context={'order': order})
    with pytest.raises(serializers.ValidationError):
        ser_invalid.is_valid(raise_exception=True)
