from decimal import Decimal
from django.utils import timezone
from rest_framework import serializers
from .models import Ingredient, InventoryStock, InventoryTransaction


class IngredientSerializer(serializers.ModelSerializer):
    current_stock = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Ingredient
        fields = [
            'id', 'name', 'category', 'unit', 'cost_per_unit', 'supplier',
            'minimum_stock', 'description', 'is_active', 'created_at', 'updated_at',
            'current_stock',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'current_stock']

    def create(self, validated_data):
        ingredient = super().create(validated_data)
        # Ensure a stock record exists for the ingredient
        InventoryStock.objects.get_or_create(ingredient=ingredient)
        return ingredient


class InventoryStockSerializer(serializers.ModelSerializer):
    ingredient_name = serializers.CharField(source='ingredient.name', read_only=True)
    unit = serializers.CharField(source='ingredient.unit', read_only=True)

    class Meta:
        model = InventoryStock
        fields = [
            'id', 'ingredient', 'ingredient_name', 'quantity', 'last_restocked',
            'expiration_date', 'updated_at', 'unit',
        ]
        read_only_fields = ['id', 'updated_at']

    def update(self, instance, validated_data):
        # Prevent direct quantity tampering through generic update; prefer adjust action
        if 'quantity' in validated_data:
            raise serializers.ValidationError({'quantity': 'Use the adjust action to modify stock quantity.'})
        return super().update(instance, validated_data)


class InventoryAdjustmentSerializer(serializers.Serializer):
    transaction_type = serializers.ChoiceField(choices=[t[0] for t in InventoryTransaction.TRANSACTION_TYPES if t[0] != 'USAGE'])
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2)
    notes = serializers.CharField(allow_blank=True, required=False)

    def validate(self, attrs):
        ttype = attrs['transaction_type']
        qty: Decimal = attrs['quantity']
        if qty == Decimal('0'):
            raise serializers.ValidationError({'quantity': 'Quantity must be non-zero.'})
        if qty < 0:
            # For RESTOCK/WASTE/RETURN enforce positive input for clarity
            if ttype in ('RESTOCK', 'WASTE', 'RETURN'):
                raise serializers.ValidationError({'quantity': 'Quantity must be positive.'})
        return attrs


class InventoryTransactionSerializer(serializers.ModelSerializer):
    ingredient_name = serializers.CharField(source='ingredient.name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = InventoryTransaction
        fields = [
            'id', 'ingredient', 'ingredient_name', 'transaction_type', 'quantity',
            'balance_after', 'notes', 'user', 'user_username', 'related_order', 'created_at'
        ]
        read_only_fields = ['id', 'balance_after', 'created_at']
