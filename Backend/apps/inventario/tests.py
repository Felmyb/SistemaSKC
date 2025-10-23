import pytest
from decimal import Decimal
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.inventario.models import Ingredient, InventoryStock, InventoryTransaction, UnitOfMeasure

User = get_user_model()


@pytest.mark.django_db
def test_ingredient_current_stock_and_low_stock_defaults():
    ing = Ingredient.objects.create(name='Tomato', unit=UnitOfMeasure.KILOGRAM, minimum_stock=Decimal('5.00'))
    assert ing.current_stock == Decimal('0.00')
    assert ing.is_low_stock() is True


@pytest.mark.django_db
def test_inventory_stock_add_and_deduct_creates_transactions():
    user = User.objects.create_user(username='inv', password='p')
    ing = Ingredient.objects.create(name='Oil', unit=UnitOfMeasure.LITER, minimum_stock=Decimal('1.00'))
    stock = InventoryStock.objects.create(ingredient=ing, quantity=Decimal('0.00'))

    stock.add_stock(Decimal('2.50'))
    assert stock.quantity == Decimal('2.50')
    assert InventoryTransaction.objects.filter(ingredient=ing, transaction_type='RESTOCK').count() == 1

    ok = stock.deduct_stock(Decimal('1.25'))
    assert ok is True
    assert stock.quantity == Decimal('1.25')
    assert InventoryTransaction.objects.filter(ingredient=ing, transaction_type='USAGE').count() == 1

    # Insufficient stock should not create a transaction
    ok2 = stock.deduct_stock(Decimal('5.00'))
    assert ok2 is False
    assert InventoryTransaction.objects.filter(ingredient=ing).count() == 2


@pytest.mark.django_db
def test_inventory_stock_str_representation():
    ing = Ingredient.objects.create(name='Cheese', unit=UnitOfMeasure.GRAM)
    stock = InventoryStock.objects.create(ingredient=ing, quantity=Decimal('500.00'))
    s = str(stock)
    assert 'Cheese' in s and '500.00' in s


@pytest.mark.django_db
def test_ingredient_str_representation():
    ing = Ingredient.objects.create(name='Milk', unit=UnitOfMeasure.LITER)
    assert 'Milk' in str(ing)
