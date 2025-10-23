"""
Tests para Endpoints REST de Inventario
======================================
RF-02: Control de inventario
"""

import pytest
from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.usuarios.models import User
from apps.inventario.models import Ingredient, InventoryStock, InventoryTransaction, UnitOfMeasure, InventoryCategory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def staff_user():
    return User.objects.create_user(
        username='inv_staff', email='invstaff@test.com', password='pass123', role='STAFF'
    )


@pytest.fixture
def customer_user():
    return User.objects.create_user(
        username='inv_customer', email='invcustomer@test.com', password='pass123', role='CUSTOMER'
    )


@pytest.mark.django_db
class TestInventoryPermissions:
    def test_inventory_requires_staff(self, api_client, customer_user):
        api_client.force_authenticate(user=customer_user)
        url = reverse('inventario:ingredient-list')
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_staff_can_access(self, api_client, staff_user):
        api_client.force_authenticate(user=staff_user)
        url = reverse('inventario:ingredient-list')
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestIngredientEndpoints:
    def test_create_ingredient_auto_stock(self, api_client, staff_user):
        api_client.force_authenticate(user=staff_user)
        url = reverse('inventario:ingredient-list')
        data = {
            'name': 'Tomato',
            'category': InventoryCategory.VEGETABLES,
            'unit': UnitOfMeasure.KILOGRAM,
            'minimum_stock': '5.00',
        }
        resp = api_client.post(url, data, format='json')
        assert resp.status_code == status.HTTP_201_CREATED
        ing = Ingredient.objects.get(name='Tomato')
        assert InventoryStock.objects.filter(ingredient=ing).exists()

    def test_low_stock_action(self, api_client, staff_user):
        api_client.force_authenticate(user=staff_user)
        ing1 = Ingredient.objects.create(name='Onion', unit=UnitOfMeasure.KILOGRAM, minimum_stock=Decimal('5.00'))
        InventoryStock.objects.create(ingredient=ing1, quantity=Decimal('2.00'))
        ing2 = Ingredient.objects.create(name='Potato', unit=UnitOfMeasure.KILOGRAM, minimum_stock=Decimal('5.00'))
        InventoryStock.objects.create(ingredient=ing2, quantity=Decimal('10.00'))

        url = reverse('inventario:ingredient-low-stock')
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        results = resp.data.get('results', resp.data)
        names = [i['name'] for i in results]
        assert 'Onion' in names and 'Potato' not in names


@pytest.mark.django_db
class TestStockAdjustments:
    def test_adjust_stock_creates_transaction(self, api_client, staff_user):
        api_client.force_authenticate(user=staff_user)
        ing = Ingredient.objects.create(name='Oil', unit=UnitOfMeasure.LITER)
        stock = InventoryStock.objects.create(ingredient=ing, quantity=Decimal('1.00'))

        # RESTOCK 2.00 => total 3.00
        url = reverse('inventario:stock-adjust', args=[stock.id])
        resp = api_client.post(url, {'transaction_type': 'RESTOCK', 'quantity': '2.00', 'notes': 'supplier X'}, format='json')
        assert resp.status_code == status.HTTP_200_OK
        stock.refresh_from_db()
        assert stock.quantity == Decimal('3.00')
        assert InventoryTransaction.objects.filter(ingredient=ing, transaction_type='RESTOCK').count() == 1

        # WASTE 1.50 => total 1.50
        resp = api_client.post(url, {'transaction_type': 'WASTE', 'quantity': '1.50'}, format='json')
        assert resp.status_code == status.HTTP_200_OK
        stock.refresh_from_db()
        assert stock.quantity == Decimal('1.50')
        assert InventoryTransaction.objects.filter(ingredient=ing, transaction_type='WASTE').count() == 1

    def test_adjust_cannot_go_negative(self, api_client, staff_user):
        api_client.force_authenticate(user=staff_user)
        ing = Ingredient.objects.create(name='Cheese', unit=UnitOfMeasure.GRAM)
        stock = InventoryStock.objects.create(ingredient=ing, quantity=Decimal('0.50'))
        url = reverse('inventario:stock-adjust', args=[stock.id])
        resp = api_client.post(url, {'transaction_type': 'WASTE', 'quantity': '1.00'}, format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestTransactionListing:
    def test_transactions_list_filter(self, api_client, staff_user):
        api_client.force_authenticate(user=staff_user)
        ing = Ingredient.objects.create(name='Flour', unit=UnitOfMeasure.KILOGRAM)
        stock = InventoryStock.objects.create(ingredient=ing, quantity=Decimal('0.00'))

        # Do some adjustments
        url_adj = reverse('inventario:stock-adjust', args=[stock.id])
        api_client.post(url_adj, {'transaction_type': 'RESTOCK', 'quantity': '5.00'}, format='json')
        api_client.post(url_adj, {'transaction_type': 'WASTE', 'quantity': '1.00'}, format='json')

        url = reverse('inventario:inventory-transaction-list')
        resp_all = api_client.get(url)
        assert resp_all.status_code == status.HTTP_200_OK
        results_all = resp_all.data.get('results', resp_all.data)
        assert len(results_all) == 2

        resp_waste = api_client.get(url, {'transaction_type': 'WASTE'})
        results_waste = resp_waste.data.get('results', resp_waste.data)
        assert len(results_waste) == 1
