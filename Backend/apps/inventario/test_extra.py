import pytest
from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.test.utils import override_settings
from apps.usuarios.models import User
from apps.inventario.models import Ingredient, InventoryStock, InventoryTransaction, UnitOfMeasure


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def staff_user():
    return User.objects.create_user(username='staff2', password='p', role='STAFF')


@pytest.mark.django_db
def test_stock_serializer_blocks_direct_quantity_update(api_client, staff_user):
    api_client.force_authenticate(user=staff_user)
    ing = Ingredient.objects.create(name='Salt', unit=UnitOfMeasure.GRAM)
    stock = InventoryStock.objects.create(ingredient=ing, quantity=Decimal('1.00'))
    url = reverse('inventario:stock-detail', args=[stock.id])
    resp = api_client.patch(url, {'quantity': '5.00'}, format='json')
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert 'quantity' in str(resp.data)


@pytest.mark.django_db
def test_adjustment_serializer_zero_and_negative_validation(api_client, staff_user):
    api_client.force_authenticate(user=staff_user)
    ing = Ingredient.objects.create(name='Sugar', unit=UnitOfMeasure.GRAM)
    stock = InventoryStock.objects.create(ingredient=ing, quantity=Decimal('1.00'))
    url = reverse('inventario:stock-adjust', args=[stock.id])

    # Zero quantity
    r0 = api_client.post(url, {'transaction_type': 'RESTOCK', 'quantity': '0'}, format='json')
    assert r0.status_code == status.HTTP_400_BAD_REQUEST

    # Negative with RESTOCK must fail
    rneg = api_client.post(url, {'transaction_type': 'RESTOCK', 'quantity': '-1'}, format='json')
    assert rneg.status_code == status.HTTP_400_BAD_REQUEST

    # ADJUSTMENT with negative allowed if not going below zero
    radj = api_client.post(url, {'transaction_type': 'ADJUSTMENT', 'quantity': '-0.50'}, format='json')
    assert radj.status_code == status.HTTP_200_OK
    stock.refresh_from_db()
    assert stock.quantity == Decimal('0.50')


@pytest.mark.django_db
def test_toggle_active_and_return_transaction(api_client, staff_user):
    api_client.force_authenticate(user=staff_user)
    ing = Ingredient.objects.create(name='Vinegar', unit=UnitOfMeasure.LITER)
    InventoryStock.objects.create(ingredient=ing, quantity=Decimal('5.00'))

    # toggle_active
    url_toggle = reverse('inventario:ingredient-toggle-active', args=[ing.id])
    r1 = api_client.post(url_toggle)
    assert r1.status_code == status.HTTP_200_OK
    ing.refresh_from_db()
    assert ing.is_active is False

    # RETURN adjustment generates transaction with negative delta
    stock = ing.stock
    url_adj = reverse('inventario:stock-adjust', args=[stock.id])
    r2 = api_client.post(url_adj, {'transaction_type': 'RETURN', 'quantity': '1.00'}, format='json')
    assert r2.status_code == status.HTTP_200_OK
    assert InventoryTransaction.objects.filter(ingredient=ing, transaction_type='RETURN').exists()


@pytest.mark.django_db
def test_transaction_str_and_stock_patch_allowed_fields(api_client, staff_user):
    api_client.force_authenticate(user=staff_user)
    ing = Ingredient.objects.create(name='Pepper', unit=UnitOfMeasure.GRAM)
    stock = InventoryStock.objects.create(ingredient=ing, quantity=Decimal('0.00'))

    # Create a transaction to test __str__
    t = InventoryTransaction.objects.create(
        ingredient=ing, transaction_type='RESTOCK', quantity=Decimal('1.00'), balance_after=Decimal('1.00')
    )
    s = str(t)
    assert 'Pepper' in s and 'Restock' in s

    # Patch allowed field (expiration_date)
    url = reverse('inventario:stock-detail', args=[stock.id])
    resp = api_client.patch(url, {'expiration_date': '2030-01-01'}, format='json')
    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_low_stock_without_pagination_branch(api_client, staff_user, monkeypatch):
    api_client.force_authenticate(user=staff_user)
    # Disable pagination on the view for this test to hit the non-paginated branch
    from apps.inventario.views import IngredientViewSet
    monkeypatch.setattr(IngredientViewSet, 'pagination_class', None, raising=False)
    ing = Ingredient.objects.create(name='Onion2', unit=UnitOfMeasure.KILOGRAM, minimum_stock=Decimal('5.00'))
    InventoryStock.objects.create(ingredient=ing, quantity=Decimal('1.00'))
    url = reverse('inventario:ingredient-low-stock')
    resp = api_client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    assert isinstance(resp.data, list)
