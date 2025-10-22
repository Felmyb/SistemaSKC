"""
Serializadores de Pedidos
=========================
"""

from rest_framework import serializers
from .models import Order, OrderItem, OrderStatus, OrderPriority
from apps.platos.models import Dish


class OrderItemSerializer(serializers.ModelSerializer):
    dish_name = serializers.CharField(source='dish.name', read_only=True)
    dish_category = serializers.CharField(source='dish.get_category_display', read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id', 'dish', 'dish_name', 'dish_category', 'quantity',
            'unit_price', 'subtotal', 'special_instructions', 'created_at'
        ]
        read_only_fields = ['id', 'subtotal', 'created_at', 'unit_price']

    def validate_dish(self, value):
        if not value.is_available:
            raise serializers.ValidationError(
                f"El platillo '{value.name}' no está disponible actualmente."
            )
        if not value.check_availability():
            raise serializers.ValidationError(
                f"Ingredientes insuficientes para '{value.name}'."
            )
        return value


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    priority_color = serializers.CharField(source='get_priority_color', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'customer_name', 'status', 'status_display', 'priority',
            'priority_display', 'priority_color', 'order_type', 'table_number',
            'total_amount', 'estimated_time', 'actual_time', 'notes', 'items',
            'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = ['id', 'total_amount', 'created_at', 'updated_at', 'completed_at']

    def validate(self, attrs):
        order_type = attrs.get('order_type')
        table_number = attrs.get('table_number')
        if order_type == 'DINE_IN' and not table_number:
            raise serializers.ValidationError({'table_number': 'Se requiere número de mesa para pedidos en el restaurante.'})
        return attrs


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['customer', 'order_type', 'table_number', 'priority', 'estimated_time', 'notes', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            dish = item_data.pop('dish')
            OrderItem.objects.create(
                order=order,
                dish=dish,
                unit_price=dish.price,
                **item_data
            )
        order.calculate_total()
        return order


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=OrderStatus.choices)
    actual_time = serializers.IntegerField(required=False, min_value=0)

    def validate_status(self, value):
        order = self.context.get('order')
        valid_transitions = {
            OrderStatus.PENDING: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
            OrderStatus.CONFIRMED: [OrderStatus.IN_PROGRESS, OrderStatus.CANCELLED],
            OrderStatus.IN_PROGRESS: [OrderStatus.READY, OrderStatus.CANCELLED],
            OrderStatus.READY: [OrderStatus.DELIVERED],
            OrderStatus.DELIVERED: [],
            OrderStatus.CANCELLED: [],
        }
        if value not in valid_transitions.get(order.status, []):
            raise serializers.ValidationError(
                f"Transición inválida de {order.get_status_display()} a {dict(OrderStatus.choices)[value]}."
            )
        return value
