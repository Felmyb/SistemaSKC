"""
Tests para Endpoints REST de Pedidos
=====================================
RF-01, RF-04: Gestión y seguimiento de pedidos
"""

import pytest
from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.usuarios.models import User
from apps.platos.models import Dish, DishCategory
from apps.inventario.models import Ingredient, InventoryStock, UnitOfMeasure
from apps.pedidos.models import Order, OrderItem, OrderStatus, OrderPriority


@pytest.fixture
def api_client():
    """Cliente API para tests."""
    return APIClient()


@pytest.fixture
def customer_user():
    """Usuario cliente autenticado."""
    return User.objects.create_user(
        username='customer',
        email='customer@test.com',
        password='pass123',
        role='CUSTOMER'
    )


@pytest.fixture
def customer2_user():
    """Segundo usuario cliente para tests de permisos."""
    return User.objects.create_user(
        username='customer2',
        email='customer2@test.com',
        password='pass123',
        role='CUSTOMER'
    )


@pytest.fixture
def staff_user():
    """Usuario staff autenticado."""
    return User.objects.create_user(
        username='staff',
        email='staff@test.com',
        password='pass123',
        role='STAFF'
    )


@pytest.fixture
def sample_dish():
    """Plato disponible con stock."""
    flour = Ingredient.objects.create(name='Flour', unit=UnitOfMeasure.KILOGRAM, cost_per_unit=Decimal('2.00'))
    InventoryStock.objects.create(ingredient=flour, quantity=Decimal('100.00'))
    
    dish = Dish.objects.create(
        name='Burger',
        description='Tasty burger',
        category=DishCategory.MAIN_COURSE,
        price=Decimal('10.00'),
        is_available=True
    )
    return dish


@pytest.fixture
def sample_order(customer_user, sample_dish):
    """Pedido de ejemplo."""
    order = Order.objects.create(
        customer=customer_user,
        order_type='DINE_IN',
        table_number='5',
        status=OrderStatus.PENDING
    )
    OrderItem.objects.create(
        order=order,
        dish=sample_dish,
        quantity=2,
        unit_price=sample_dish.price
    )
    order.calculate_total()
    return order


@pytest.mark.django_db
class TestOrderViewSetPermissions:
    """Tests de permisos del ViewSet de pedidos."""
    
    def test_list_orders_requires_authentication(self, api_client):
        """Listar pedidos requiere autenticación."""
        url = reverse('pedidos:order-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_customer_can_list_own_orders(self, api_client, customer_user, sample_order):
        """Clientes pueden listar sus propios pedidos."""
        api_client.force_authenticate(user=customer_user)
        url = reverse('pedidos:order-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        results = response.data.get('results', response.data)
        assert len(results) == 1
        assert results[0]['id'] == sample_order.id
    
    def test_customer_cannot_see_other_orders(self, api_client, customer_user, customer2_user, sample_dish):
        """Clientes no ven pedidos de otros clientes."""
        # Crear pedido de customer2
        order2 = Order.objects.create(
            customer=customer2_user,
            order_type='TAKEOUT'
        )
        OrderItem.objects.create(order=order2, dish=sample_dish, quantity=1, unit_price=sample_dish.price)
        
        # customer1 intenta listar
        api_client.force_authenticate(user=customer_user)
        url = reverse('pedidos:order-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        results = response.data.get('results', response.data)
        # No debe ver el pedido de customer2
        assert len(results) == 0
    
    def test_staff_can_see_all_orders(self, api_client, staff_user, customer_user, sample_order):
        """Staff puede ver todos los pedidos."""
        api_client.force_authenticate(user=staff_user)
        url = reverse('pedidos:order-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        results = response.data.get('results', response.data)
        assert len(results) >= 1
    
    def test_customer_can_create_order(self, api_client, customer_user, sample_dish):
        """Clientes pueden crear pedidos."""
        api_client.force_authenticate(user=customer_user)
        url = reverse('pedidos:order-list')
        data = {
            'customer': customer_user.id,
            'order_type': 'DINE_IN',
            'table_number': '10',
            'priority': OrderPriority.MEDIUM,
            'estimated_time': 20,
            'notes': 'Sin cebolla',
            'items': [
                {
                    'dish': sample_dish.id,
                    'quantity': 2,
                    'special_instructions': 'Extra queso'
                }
            ]
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Order.objects.filter(customer=customer_user).count() == 1
        order = Order.objects.get(customer=customer_user)
        assert order.items.count() == 1
        assert order.total_amount == Decimal('20.00')  # 2 * 10.00
    
    def test_customer_cannot_update_order_status(self, api_client, customer_user, sample_order):
        """Clientes no pueden actualizar estado de pedidos."""
        api_client.force_authenticate(user=customer_user)
        url = reverse('pedidos:order-update-status', args=[sample_order.id])
        data = {'status': OrderStatus.CONFIRMED}
        response = api_client.patch(url, data, format='json')
        # Depende de la implementación de permisos, debería ser 403
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_405_METHOD_NOT_ALLOWED]
    
    def test_staff_can_update_order_status(self, api_client, staff_user, sample_order):
        """Staff puede actualizar estado de pedidos."""
        api_client.force_authenticate(user=staff_user)
        url = reverse('pedidos:order-update-status', args=[sample_order.id])
        data = {'status': OrderStatus.CONFIRMED}
        response = api_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        sample_order.refresh_from_db()
        assert sample_order.status == OrderStatus.CONFIRMED
    
    def test_customer_can_retrieve_own_order(self, api_client, customer_user, sample_order):
        """Clientes pueden ver detalle de sus pedidos."""
        api_client.force_authenticate(user=customer_user)
        url = reverse('pedidos:order-detail', args=[sample_order.id])
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == sample_order.id
        assert 'items' in response.data
    
    def test_customer_cannot_retrieve_other_order(self, api_client, customer_user, customer2_user, sample_dish):
        """Clientes no pueden ver pedidos de otros."""
        # Pedido de customer2
        order2 = Order.objects.create(customer=customer2_user, order_type='TAKEOUT')
        OrderItem.objects.create(order=order2, dish=sample_dish, quantity=1, unit_price=sample_dish.price)
        
        # customer1 intenta acceder
        api_client.force_authenticate(user=customer_user)
        url = reverse('pedidos:order-detail', args=[order2.id])
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestOrderViewSetFilters:
    """Tests de filtros y búsqueda."""
    
    @pytest.fixture(autouse=True)
    def setup_orders(self, customer_user, sample_dish):
        """Crea varios pedidos para filtrar."""
        Order.objects.create(
            customer=customer_user,
            order_type='DINE_IN',
            table_number='1',
            status=OrderStatus.PENDING,
            priority=OrderPriority.HIGH
        )
        Order.objects.create(
            customer=customer_user,
            order_type='TAKEOUT',
            status=OrderStatus.DELIVERED,
            priority=OrderPriority.LOW
        )
        Order.objects.create(
            customer=customer_user,
            order_type='DELIVERY',
            status=OrderStatus.IN_PROGRESS,
            priority=OrderPriority.URGENT
        )
    
    def test_filter_by_status(self, api_client, customer_user):
        """Filtrar pedidos por estado."""
        api_client.force_authenticate(user=customer_user)
        url = reverse('pedidos:order-list')
        response = api_client.get(url, {'status': OrderStatus.PENDING})
        assert response.status_code == status.HTTP_200_OK
        results = response.data.get('results', response.data)
        assert len(results) == 1
        assert results[0]['status'] == OrderStatus.PENDING
    
    def test_filter_by_priority(self, api_client, customer_user):
        """Filtrar pedidos por prioridad."""
        api_client.force_authenticate(user=customer_user)
        url = reverse('pedidos:order-list')
        response = api_client.get(url, {'priority': OrderPriority.HIGH})
        assert response.status_code == status.HTTP_200_OK
        results = response.data.get('results', response.data)
        assert len(results) == 1
    
    def test_filter_by_order_type(self, api_client, customer_user):
        """Filtrar pedidos por tipo."""
        api_client.force_authenticate(user=customer_user)
        url = reverse('pedidos:order-list')
        response = api_client.get(url, {'order_type': 'TAKEOUT'})
        assert response.status_code == status.HTTP_200_OK
        results = response.data.get('results', response.data)
        assert len(results) == 1
    
    def test_search_by_table_number(self, api_client, customer_user):
        """Buscar pedidos por mesa."""
        api_client.force_authenticate(user=customer_user)
        url = reverse('pedidos:order-list')
        response = api_client.get(url, {'search': '1'})
        assert response.status_code == status.HTTP_200_OK
        results = response.data.get('results', response.data)
        assert len(results) >= 1
    
    def test_ordering_by_created_at(self, api_client, customer_user):
        """Ordenar pedidos por fecha."""
        api_client.force_authenticate(user=customer_user)
        url = reverse('pedidos:order-list')
        response = api_client.get(url, {'ordering': '-created_at'})
        assert response.status_code == status.HTTP_200_OK
        # Por defecto ya está ordenado así


@pytest.mark.django_db
class TestOrderViewSetCustomActions:
    """Tests de acciones personalizadas."""
    
    def test_active_orders(self, api_client, staff_user, customer_user, sample_dish):
        """Obtener pedidos activos."""
        # Crear pedidos en diferentes estados
        Order.objects.create(customer=customer_user, status=OrderStatus.PENDING, order_type='DINE_IN')
        Order.objects.create(customer=customer_user, status=OrderStatus.IN_PROGRESS, order_type='DINE_IN')
        Order.objects.create(customer=customer_user, status=OrderStatus.DELIVERED, order_type='DINE_IN')
        
        api_client.force_authenticate(user=staff_user)
        url = reverse('pedidos:order-active')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        results = response.data.get('results', response.data)
        # Solo activos (no delivered)
        assert len(results) == 2
    
    def test_history_orders(self, api_client, customer_user, sample_dish):
        """Obtener historial de pedidos."""
        Order.objects.create(customer=customer_user, status=OrderStatus.DELIVERED, order_type='DINE_IN')
        Order.objects.create(customer=customer_user, status=OrderStatus.CANCELLED, order_type='DINE_IN')
        Order.objects.create(customer=customer_user, status=OrderStatus.PENDING, order_type='DINE_IN')
        
        api_client.force_authenticate(user=customer_user)
        url = reverse('pedidos:order-history')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        results = response.data.get('results', response.data)
        # Solo completados/cancelados
        assert len(results) == 2
    
    def test_cancel_order(self, api_client, customer_user, sample_order):
        """Cancelar un pedido pendiente."""
        api_client.force_authenticate(user=customer_user)
        url = reverse('pedidos:order-cancel', args=[sample_order.id])
        response = api_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        sample_order.refresh_from_db()
        assert sample_order.status == OrderStatus.CANCELLED
    
    def test_cannot_cancel_delivered_order(self, api_client, customer_user, sample_order):
        """No se puede cancelar un pedido ya entregado."""
        sample_order.status = OrderStatus.DELIVERED
        sample_order.save()
        
        api_client.force_authenticate(user=customer_user)
        url = reverse('pedidos:order-cancel', args=[sample_order.id])
        response = api_client.post(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_stats_endpoint_staff_only(self, api_client, staff_user, customer_user, sample_order):
        """Estadísticas solo para staff."""
        # Cliente no puede acceder
        api_client.force_authenticate(user=customer_user)
        url = reverse('pedidos:order-stats')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Staff sí puede
        api_client.force_authenticate(user=staff_user)
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'total_orders' in response.data
        assert 'by_status' in response.data


@pytest.mark.django_db
class TestOrderStatusTransitions:
    """Tests de transiciones de estado."""
    
    def test_valid_status_transition(self, api_client, staff_user, sample_order):
        """Transiciones válidas de estado."""
        api_client.force_authenticate(user=staff_user)
        url = reverse('pedidos:order-update-status', args=[sample_order.id])
        
        # PENDING → CONFIRMED
        response = api_client.patch(url, {'status': OrderStatus.CONFIRMED}, format='json')
        assert response.status_code == status.HTTP_200_OK
        sample_order.refresh_from_db()
        assert sample_order.status == OrderStatus.CONFIRMED
        
        # CONFIRMED → IN_PROGRESS
        response = api_client.patch(url, {'status': OrderStatus.IN_PROGRESS}, format='json')
        assert response.status_code == status.HTTP_200_OK
    
    def test_invalid_status_transition(self, api_client, staff_user, sample_order):
        """Transiciones inválidas deben fallar."""
        api_client.force_authenticate(user=staff_user)
        url = reverse('pedidos:order-update-status', args=[sample_order.id])
        
        # PENDING → READY (saltar pasos)
        response = api_client.patch(url, {'status': OrderStatus.READY}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_delivered_sets_completed_at(self, api_client, staff_user, sample_order):
        """Marcar como entregado registra timestamp."""
        api_client.force_authenticate(user=staff_user)
        url = reverse('pedidos:order-update-status', args=[sample_order.id])
        
        # Avanzar hasta READY
        sample_order.status = OrderStatus.READY
        sample_order.save()
        
        # READY → DELIVERED
        response = api_client.patch(url, {'status': OrderStatus.DELIVERED, 'actual_time': 25}, format='json')
        assert response.status_code == status.HTTP_200_OK
        sample_order.refresh_from_db()
        assert sample_order.status == OrderStatus.DELIVERED
        assert sample_order.completed_at is not None
        assert sample_order.actual_time == 25


@pytest.mark.django_db
class TestOrderValidations:
    """Tests de validaciones del serializer."""
    
    def test_dine_in_requires_table_number(self, api_client, customer_user, sample_dish):
        """Pedidos dine-in requieren número de mesa."""
        api_client.force_authenticate(user=customer_user)
        url = reverse('pedidos:order-list')
        data = {
            'customer': customer_user.id,
            'order_type': 'DINE_IN',
            # Falta table_number
            'items': [{'dish': sample_dish.id, 'quantity': 1}]
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'table_number' in str(response.data)
    
    def test_unavailable_dish_validation(self, api_client, customer_user, sample_dish):
        """No se pueden pedir platos no disponibles."""
        sample_dish.is_available = False
        sample_dish.save()
        
        api_client.force_authenticate(user=customer_user)
        url = reverse('pedidos:order-list')
        data = {
            'customer': customer_user.id,
            'order_type': 'TAKEOUT',
            'items': [{'dish': sample_dish.id, 'quantity': 1}]
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
