"""
Serializers para Platos
========================
RF-01: Gestión del menú digital
"""

from rest_framework import serializers
from .models import Dish, RecipeItem
from apps.inventario.models import Ingredient


class RecipeItemSerializer(serializers.ModelSerializer):
    """
    Serializer para RecipeItem (ingredientes de una receta).
    RF-02: Control de inventario y recetas.
    """
    ingredient_name = serializers.CharField(source='ingredient.name', read_only=True)
    ingredient_unit = serializers.CharField(source='ingredient.unit', read_only=True)
    is_available = serializers.SerializerMethodField()

    class Meta:
        model = RecipeItem
        fields = [
            'id', 'ingredient', 'ingredient_name', 'ingredient_unit',
            'quantity', 'notes', 'is_available'
        ]
        read_only_fields = ['id']

    def get_is_available(self, obj):
        """Verifica si hay suficiente stock del ingrediente."""
        return obj.check_availability()


class DishListSerializer(serializers.ModelSerializer):
    """
    Serializer para listar platos (sin detalles de receta).
    Optimizado para listados y búsquedas.
    """
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    is_in_stock = serializers.SerializerMethodField()

    class Meta:
        model = Dish
        fields = [
            'id', 'name', 'description', 'category', 'category_display',
            'price', 'preparation_time', 'image', 'is_available',
            'is_vegetarian', 'is_vegan', 'popularity_score', 'is_in_stock'
        ]
        read_only_fields = ['id', 'popularity_score']

    def get_is_in_stock(self, obj):
        """Verifica disponibilidad basada en inventario."""
        return obj.check_availability()


class DishDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detallado para platos con receta completa.
    RF-01, RF-02: Menú y recetas.
    """
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    recipe_items = RecipeItemSerializer(many=True, read_only=True)
    is_in_stock = serializers.SerializerMethodField()
    estimated_cost = serializers.SerializerMethodField()

    class Meta:
        model = Dish
        fields = [
            'id', 'name', 'description', 'category', 'category_display',
            'price', 'preparation_time', 'image', 'is_available',
            'is_vegetarian', 'is_vegan', 'allergens', 'popularity_score',
            'recipe_items', 'is_in_stock', 'estimated_cost',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'popularity_score', 'created_at', 'updated_at']

    def get_is_in_stock(self, obj):
        """Verifica disponibilidad basada en inventario."""
        return obj.check_availability()

    def get_estimated_cost(self, obj):
        """Calcula el costo estimado de producción."""
        return float(obj.calculate_cost())


class DishCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear/actualizar platos con manejo de receta.
    Solo staff/admin pueden usar este serializer.
    """
    recipe_items = RecipeItemSerializer(many=True, required=False)

    class Meta:
        model = Dish
        fields = [
            'id', 'name', 'description', 'category', 'price',
            'preparation_time', 'image', 'is_available',
            'is_vegetarian', 'is_vegan', 'allergens',
            'recipe_items'
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        """Crea un plato con sus items de receta."""
        recipe_items_data = validated_data.pop('recipe_items', [])
        dish = Dish.objects.create(**validated_data)
        
        for item_data in recipe_items_data:
            RecipeItem.objects.create(dish=dish, **item_data)
        
        return dish

    def update(self, instance, validated_data):
        """Actualiza un plato y opcionalmente su receta."""
        recipe_items_data = validated_data.pop('recipe_items', None)
        
        # Actualizar campos del plato
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Si se proveen recipe_items, reemplazar los existentes
        if recipe_items_data is not None:
            instance.recipe_items.all().delete()
            for item_data in recipe_items_data:
                RecipeItem.objects.create(dish=instance, **item_data)
        
        return instance

    def validate_price(self, value):
        """Valida que el precio sea positivo."""
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor que cero.")
        return value

    def validate(self, data):
        """Validaciones a nivel de objeto."""
        # Si es vegano, debe ser vegetariano también
        if data.get('is_vegan', False) and not data.get('is_vegetarian', False):
            data['is_vegetarian'] = True
        
        return data
