import pytest
from decimal import Decimal
from apps.inventario.models import Ingredient, InventoryStock, UnitOfMeasure
from apps.platos.models import Dish, DishCategory, RecipeItem


@pytest.mark.django_db
def test_dish_cost_and_availability_checks():
    # Ingredients
    flour = Ingredient.objects.create(name='Flour', unit=UnitOfMeasure.KILOGRAM, cost_per_unit=Decimal('2.00'))
    milk = Ingredient.objects.create(name='Milk', unit=UnitOfMeasure.LITER, cost_per_unit=Decimal('1.50'))

    InventoryStock.objects.create(ingredient=flour, quantity=Decimal('1.00'))
    InventoryStock.objects.create(ingredient=milk, quantity=Decimal('0.50'))

    # Dish with two recipe items
    dish = Dish.objects.create(name='Pancake', description='Yum', category=DishCategory.MAIN_COURSE, price=Decimal('10.00'))
    ri1 = RecipeItem.objects.create(dish=dish, ingredient=flour, quantity=Decimal('0.20'))
    ri2 = RecipeItem.objects.create(dish=dish, ingredient=milk, quantity=Decimal('0.30'))

    # Availability: enough stock for both
    assert ri1.check_availability() is True
    assert ri2.check_availability() is True
    assert dish.check_availability() is True

    # Cost
    assert dish.calculate_cost() == Decimal('2.00') * Decimal('0.20') + Decimal('1.50') * Decimal('0.30')

    # Reduce milk stock to force unavailability
    stock_milk = milk.stock
    stock_milk.quantity = Decimal('0.10')
    stock_milk.save()
    assert dish.check_availability() is False


@pytest.mark.django_db
def test_recipe_item_str():
    ing = Ingredient.objects.create(name='Sugar', unit=UnitOfMeasure.GRAM)
    InventoryStock.objects.create(ingredient=ing, quantity=Decimal('100.00'))
    dish = Dish.objects.create(name='Cake', description='Sweet', price=Decimal('5.00'))
    ri = RecipeItem.objects.create(dish=dish, ingredient=ing, quantity=Decimal('10.00'))
    s = str(ri)
    assert 'Cake' in s and 'Sugar' in s
