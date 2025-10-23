from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IngredientViewSet, InventoryStockViewSet, InventoryTransactionViewSet


router = DefaultRouter()
router.register(r'ingredients', IngredientViewSet, basename='ingredient')
router.register(r'stocks', InventoryStockViewSet, basename='stock')
router.register(r'transactions', InventoryTransactionViewSet, basename='inventory-transaction')


app_name = 'inventario'
urlpatterns = [
    path('inventory/', include(router.urls)),
]
