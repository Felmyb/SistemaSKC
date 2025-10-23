import pytest
from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.usuarios.models import User
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


# ============================================================================
# TESTS DE ENDPOINTS REST - ViewSet de Platos
# ============================================================================

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
    """Plato de ejemplo con receta."""
    flour = Ingredient.objects.create(name='Flour', unit=UnitOfMeasure.KILOGRAM, cost_per_unit=Decimal('2.00'))
    InventoryStock.objects.create(ingredient=flour, quantity=Decimal('10.00'))
    
    dish = Dish.objects.create(
        name='Pancakes',
        description='Delicious pancakes',
        category=DishCategory.MAIN_COURSE,
        price=Decimal('8.50'),
        preparation_time=15,
        is_available=True,
        is_vegetarian=True
    )
    RecipeItem.objects.create(dish=dish, ingredient=flour, quantity=Decimal('0.20'))
    return dish


@pytest.mark.django_db
class TestDishViewSetPermissions:
    """Tests de permisos del ViewSet."""
    
    def test_list_dishes_requires_authentication(self, api_client):
        """Listar platos requiere autenticación."""
        url = reverse('platos:dish-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_customer_can_list_dishes(self, api_client, customer_user, sample_dish):
        """Clientes pueden listar platos."""
        api_client.force_authenticate(user=customer_user)
        url = reverse('platos:dish-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        # DRF pagina por defecto, verificar results
        results = response.data.get('results', response.data)
        assert len(results) == 1
    
    def test_customer_can_retrieve_dish(self, api_client, customer_user, sample_dish):
        """Clientes pueden ver detalle de plato."""
        api_client.force_authenticate(user=customer_user)
        url = reverse('platos:dish-detail', args=[sample_dish.id])
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Pancakes'
        assert 'recipe_items' in response.data
    
    def test_customer_cannot_create_dish(self, api_client, customer_user):
        """Clientes no pueden crear platos."""
        api_client.force_authenticate(user=customer_user)
        url = reverse('platos:dish-list')
        data = {
            'name': 'New Dish',
            'description': 'Test',
            'category': DishCategory.APPETIZER,
            'price': '5.00'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_staff_can_create_dish(self, api_client, staff_user):
        """Staff puede crear platos."""
        api_client.force_authenticate(user=staff_user)
        url = reverse('platos:dish-list')
        data = {
            'name': 'New Dish',
            'description': 'Test dish',
            'category': DishCategory.APPETIZER,
            'price': '5.00',
            'preparation_time': 10
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Dish.objects.filter(name='New Dish').exists()
    
    def test_customer_cannot_update_dish(self, api_client, customer_user, sample_dish):
        """Clientes no pueden actualizar platos."""
        api_client.force_authenticate(user=customer_user)
        url = reverse('platos:dish-detail', args=[sample_dish.id])
        data = {'price': '10.00'}
        response = api_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_staff_can_update_dish(self, api_client, staff_user, sample_dish):
        """Staff puede actualizar platos."""
        api_client.force_authenticate(user=staff_user)
        url = reverse('platos:dish-detail', args=[sample_dish.id])
        data = {'price': '10.00'}
        response = api_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        sample_dish.refresh_from_db()
        assert sample_dish.price == Decimal('10.00')
    
    def test_staff_can_delete_dish(self, api_client, staff_user, sample_dish):
        """Staff puede eliminar platos."""
        api_client.force_authenticate(user=staff_user)
        url = reverse('platos:dish-detail', args=[sample_dish.id])
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Dish.objects.filter(id=sample_dish.id).exists()


@pytest.mark.django_db
class TestDishViewSetFilters:
    """Tests de filtros y búsqueda."""
    
    @pytest.fixture(autouse=True)
    def setup_dishes(self):
        """Crea varios platos para filtrar."""
        Dish.objects.create(
            name='Salad',
            description='Fresh salad',
            category=DishCategory.SALAD,
            price=Decimal('5.00'),
            is_available=True,
            is_vegetarian=True,
            is_vegan=True
        )
        Dish.objects.create(
            name='Steak',
            description='Grilled steak',
            category=DishCategory.MAIN_COURSE,
            price=Decimal('15.00'),
            is_available=True,
            is_vegetarian=False
        )
        Dish.objects.create(
            name='Ice Cream',
            description='Vanilla ice cream',
            category=DishCategory.DESSERT,
            price=Decimal('4.00'),
            is_available=False
        )
    
    def test_filter_by_category(self, api_client, customer_user):
        """Filtrar platos por categoría."""
        api_client.force_authenticate(user=customer_user)
        url = reverse('platos:dish-list')
        response = api_client.get(url, {'category': DishCategory.SALAD})
        assert response.status_code == status.HTTP_200_OK
        results = response.data.get('results', response.data)
        assert len(results) == 1
        assert results[0]['name'] == 'Salad'
    
    def test_filter_by_availability(self, api_client, customer_user):
        """Filtrar platos disponibles."""
        api_client.force_authenticate(user=customer_user)
        url = reverse('platos:dish-list')
        response = api_client.get(url, {'is_available': 'true'})
        assert response.status_code == status.HTTP_200_OK
        results = response.data.get('results', response.data)
        assert len(results) == 2
    
    def test_filter_by_vegetarian(self, api_client, customer_user):
        """Filtrar platos vegetarianos."""
        api_client.force_authenticate(user=customer_user)
        url = reverse('platos:dish-list')
        response = api_client.get(url, {'is_vegetarian': 'true'})
        assert response.status_code == status.HTTP_200_OK
        results = response.data.get('results', response.data)
        assert len(results) == 1
    
    def test_filter_by_vegan(self, api_client, customer_user):
        """Filtrar platos veganos."""
        api_client.force_authenticate(user=customer_user)
        url = reverse('platos:dish-list')
        response = api_client.get(url, {'is_vegan': 'true'})
        assert response.status_code == status.HTTP_200_OK
        results = response.data.get('results', response.data)
        assert len(results) == 1
        assert results[0]['name'] == 'Salad'
    
    def test_search_by_name(self, api_client, customer_user):
        """Buscar platos por nombre."""
        api_client.force_authenticate(user=customer_user)
        url = reverse('platos:dish-list')
        response = api_client.get(url, {'search': 'steak'})
        assert response.status_code == status.HTTP_200_OK
        results = response.data.get('results', response.data)
        assert len(results) == 1
        assert results[0]['name'] == 'Steak'
    
    def test_ordering_by_price(self, api_client, customer_user):
        """Ordenar platos por precio."""
        api_client.force_authenticate(user=customer_user)
        url = reverse('platos:dish-list')
        response = api_client.get(url, {'ordering': 'price'})
        assert response.status_code == status.HTTP_200_OK
        results = response.data.get('results', response.data)
        prices = [Decimal(d['price']) for d in results]
        assert prices == sorted(prices)


@pytest.mark.django_db
class TestDishViewSetCustomActions:
    """Tests de acciones personalizadas."""
    
    def test_popular_dishes(self, api_client, customer_user):
        """Obtener platos populares."""
        # Crear platos con diferentes scores
        Dish.objects.create(name='Popular 1', description='Test', price=Decimal('10.00'), 
                           is_available=True, popularity_score=100)
        Dish.objects.create(name='Popular 2', description='Test', price=Decimal('10.00'), 
                           is_available=True, popularity_score=50)
        Dish.objects.create(name='Unpopular', description='Test', price=Decimal('10.00'), 
                           is_available=True, popularity_score=10)
        
        api_client.force_authenticate(user=customer_user)
        url = reverse('platos:dish-popular')
        response = api_client.get(url, {'limit': 2})
        assert response.status_code == status.HTTP_200_OK
        # Endpoint popular devuelve lista directa, no paginada
        assert len(response.data) == 2
        assert response.data[0]['name'] == 'Popular 1'
    
    def test_categories_endpoint(self, api_client, customer_user):
        """Obtener categorías con conteo."""
        Dish.objects.create(name='Dish 1', description='Test', price=Decimal('10.00'), 
                           category=DishCategory.SALAD, is_available=True)
        Dish.objects.create(name='Dish 2', description='Test', price=Decimal('10.00'), 
                           category=DishCategory.SALAD, is_available=True)
        
        api_client.force_authenticate(user=customer_user)
        url = reverse('platos:dish-categories')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        salad_cat = next((c for c in response.data if c['code'] == DishCategory.SALAD), None)
        assert salad_cat is not None
        assert salad_cat['count'] == 2
    
    def test_mark_unavailable(self, api_client, staff_user, sample_dish):
        """Marcar plato como no disponible."""
        api_client.force_authenticate(user=staff_user)
        url = reverse('platos:dish-mark-unavailable', args=[sample_dish.id])
        response = api_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        sample_dish.refresh_from_db()
        assert sample_dish.is_available is False
    
    def test_mark_available(self, api_client, staff_user, sample_dish):
        """Marcar plato como disponible."""
        sample_dish.is_available = False
        sample_dish.save()
        
        api_client.force_authenticate(user=staff_user)
        url = reverse('platos:dish-mark-available', args=[sample_dish.id])
        response = api_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        sample_dish.refresh_from_db()
        assert sample_dish.is_available is True


@pytest.mark.django_db
class TestDishSerializers:
    """Tests de serializers."""
    
    def test_dish_with_recipe_creation(self, api_client, staff_user):
        """Crear plato con receta incluida."""
        flour = Ingredient.objects.create(name='Flour', unit=UnitOfMeasure.KILOGRAM, cost_per_unit=Decimal('2.00'))
        InventoryStock.objects.create(ingredient=flour, quantity=Decimal('10.00'))
        
        api_client.force_authenticate(user=staff_user)
        url = reverse('platos:dish-list')
        data = {
            'name': 'Bread',
            'description': 'Fresh bread',
            'category': DishCategory.SIDE_DISH,
            'price': '3.00',
            'recipe_items': [
                {'ingredient': flour.id, 'quantity': '0.50', 'notes': 'Main ingredient'}
            ]
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        dish = Dish.objects.get(name='Bread')
        assert dish.recipe_items.count() == 1
    
    def test_vegan_automatically_vegetarian(self, api_client, staff_user):
        """Platos veganos se marcan automáticamente como vegetarianos."""
        api_client.force_authenticate(user=staff_user)
        url = reverse('platos:dish-list')
        data = {
            'name': 'Vegan Salad',
            'description': 'Test',
            'category': DishCategory.SALAD,
            'price': '5.00',
            'is_vegan': True,
            'is_vegetarian': False  # Debería forzarse a True
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        dish = Dish.objects.get(name='Vegan Salad')
        assert dish.is_vegetarian is True
