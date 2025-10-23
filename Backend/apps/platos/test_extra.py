import pytest
from decimal import Decimal
from apps.inventario.models import Ingredient, InventoryStock, UnitOfMeasure
from apps.platos.models import Dish, RecipeItem, DishCategory
from apps.platos.serializers import DishCreateUpdateSerializer


@pytest.mark.django_db
def test_recipeitem_availability_no_stock_and_true_path():
    ing = Ingredient.objects.create(name='Flour2', unit=UnitOfMeasure.KILOGRAM)
    dish = Dish.objects.create(name='Bread', description='desc', category=DishCategory.MAIN_COURSE, price=Decimal('1.00'))
    ri = RecipeItem.objects.create(dish=dish, ingredient=ing, quantity=Decimal('1.00'))
    # No stock -> False
    assert ri.check_availability() is False
    # Add stock -> True
    InventoryStock.objects.create(ingredient=ing, quantity=Decimal('2.00'))
    assert ri.check_availability() is True
    # Dish with recipe item available -> check_availability True
    assert dish.check_availability() is True

    # Dish __str__ coverage
    assert dish.name in str(dish)


@pytest.mark.django_db
def test_dish_createupdate_validations():
    data = {
        'name': 'Vegan Salad', 'description': 'desc', 'category': DishCategory.SALAD,
        'price': Decimal('10.00'), 'is_vegan': True, 'is_vegetarian': False
    }
    ser = DishCreateUpdateSerializer(data=data)
    assert ser.is_valid(), ser.errors
    assert ser.validated_data['is_vegetarian'] is True

    # Invalid price <= 0
    ser2 = DishCreateUpdateSerializer(data={**data, 'price': Decimal('0.00')})
    assert ser2.is_valid() is False


@pytest.mark.django_db
def test_validate_price_direct():
    from rest_framework import serializers
    s = DishCreateUpdateSerializer()
    with pytest.raises(serializers.ValidationError):
        s.validate_price(Decimal('0'))
