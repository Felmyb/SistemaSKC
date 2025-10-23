"""
Views (ViewSets) para Platos
=============================
RF-01: Gestión del menú digital
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Dish, DishCategory
from .serializers import (
    DishListSerializer,
    DishDetailSerializer,
    DishCreateUpdateSerializer
)
from .permissions import IsStaffOrReadOnly


class DishViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión completa de platos del menú.
    
    RF-01: Gestión del menú digital
    - list: Ver todos los platos (cualquier usuario autenticado)
    - retrieve: Ver detalle de un plato con receta
    - create: Crear plato (solo staff/admin)
    - update/partial_update: Modificar plato (solo staff/admin)
    - destroy: Eliminar plato (solo staff/admin)
    
    Filtros disponibles:
    - category: Filtrar por categoría
    - is_available: Filtrar por disponibilidad
    - is_vegetarian: Filtrar vegetarianos
    - is_vegan: Filtrar veganos
    - search: Buscar por nombre o descripción
    - ordering: Ordenar por precio, popularidad, nombre
    """
    queryset = Dish.objects.all().prefetch_related('recipe_items__ingredient')
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_available', 'is_vegetarian', 'is_vegan']
    search_fields = ['name', 'description', 'allergens']
    ordering_fields = ['name', 'price', 'popularity_score', 'preparation_time', 'created_at']
    ordering = ['category', 'name']

    def get_serializer_class(self):
        """Devuelve el serializer apropiado según la acción."""
        if self.action == 'list':
            return DishListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return DishCreateUpdateSerializer
        return DishDetailSerializer

    @swagger_auto_schema(
        operation_description="Lista todos los platos del menú con filtros opcionales",
        manual_parameters=[
            openapi.Parameter('category', openapi.IN_QUERY, description="Filtrar por categoría", type=openapi.TYPE_STRING),
            openapi.Parameter('is_available', openapi.IN_QUERY, description="Filtrar por disponibilidad", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('is_vegetarian', openapi.IN_QUERY, description="Solo platos vegetarianos", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('is_vegan', openapi.IN_QUERY, description="Solo platos veganos", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('search', openapi.IN_QUERY, description="Buscar en nombre, descripción o alérgenos", type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Ordenar por: name, price, popularity_score, -price, etc.", type=openapi.TYPE_STRING),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Obtiene el detalle completo de un plato incluyendo su receta"
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Crea un nuevo plato (solo staff/admin)",
        request_body=DishCreateUpdateSerializer
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Actualiza un plato existente (solo staff/admin)",
        request_body=DishCreateUpdateSerializer
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Actualiza parcialmente un plato (solo staff/admin)",
        request_body=DishCreateUpdateSerializer
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Elimina un plato del menú (solo staff/admin)"
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        method='get',
        operation_description="Obtiene platos populares (RF-06: Recomendaciones)",
        manual_parameters=[
            openapi.Parameter('limit', openapi.IN_QUERY, description="Número de platos a retornar (default: 10)", type=openapi.TYPE_INTEGER),
        ]
    )
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """
        Endpoint personalizado para obtener platos populares.
        RF-06: Sistema de recomendaciones.
        """
        limit = int(request.query_params.get('limit', 10))
        popular_dishes = self.queryset.filter(is_available=True).order_by('-popularity_score')[:limit]
        serializer = DishListSerializer(popular_dishes, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        method='get',
        operation_description="Obtiene las categorías disponibles con conteo de platos"
    )
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """
        Endpoint para obtener todas las categorías con conteo de platos.
        """
        categories_data = []
        for category_code, category_name in DishCategory.choices:
            count = self.queryset.filter(category=category_code, is_available=True).count()
            categories_data.append({
                'code': category_code,
                'name': category_name,
                'count': count
            })
        return Response(categories_data)

    @swagger_auto_schema(
        method='post',
        operation_description="Marca un plato como no disponible (solo staff/admin)"
    )
    @action(detail=True, methods=['post'])
    def mark_unavailable(self, request, pk=None):
        """
        Marca un plato como no disponible rápidamente.
        RF-01: Gestión de disponibilidad.
        """
        dish = self.get_object()
        dish.is_available = False
        dish.save()
        serializer = self.get_serializer(dish)
        return Response(serializer.data)

    @swagger_auto_schema(
        method='post',
        operation_description="Marca un plato como disponible (solo staff/admin)"
    )
    @action(detail=True, methods=['post'])
    def mark_available(self, request, pk=None):
        """
        Marca un plato como disponible.
        RF-01: Gestión de disponibilidad.
        """
        dish = self.get_object()
        dish.is_available = True
        dish.save()
        serializer = self.get_serializer(dish)
        return Response(serializer.data)
