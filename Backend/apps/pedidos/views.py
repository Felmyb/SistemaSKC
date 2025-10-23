"""
Views (ViewSets) para Pedidos
==============================
RF-01, RF-04: Gestión de pedidos y seguimiento
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone

from .models import Order, OrderStatus, OrderPriority
from .serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    OrderStatusUpdateSerializer
)
from .permissions import IsOwnerOrStaff, IsStaffOrReadOnlyOwn, IsStaffOnly


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión completa de pedidos.
    
    RF-01, RF-04: Gestión y seguimiento de pedidos
    
    Permisos:
    - Clientes: pueden crear pedidos y ver solo los suyos
    - Staff/Admin: pueden ver y modificar todos los pedidos
    
    Filtros disponibles:
    - status: Filtrar por estado (PENDING, CONFIRMED, IN_PROGRESS, READY, DELIVERED, CANCELLED)
    - priority: Filtrar por prioridad (LOW, MEDIUM, HIGH, URGENT)
    - order_type: Filtrar por tipo (DINE_IN, TAKEOUT, DELIVERY)
    - customer: Filtrar por cliente (solo staff)
    - created_at: Rango de fechas
    
    Ordenamiento:
    - created_at, updated_at, total_amount, priority, status
    """
    queryset = Order.objects.all().select_related('customer').prefetch_related('items__dish')
    permission_classes = [IsStaffOrReadOnlyOwn]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'order_type', 'customer']
    search_fields = ['notes', 'table_number', 'customer__username']
    ordering_fields = ['created_at', 'updated_at', 'total_amount', 'priority', 'status']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Devuelve el serializer apropiado según la acción."""
        if self.action == 'create':
            return OrderCreateSerializer
        elif self.action == 'update_status':
            return OrderStatusUpdateSerializer
        return OrderSerializer

    def get_queryset(self):
        """
        Filtrar pedidos según el rol del usuario:
        - Clientes solo ven sus propios pedidos
        - Staff/Admin ven todos los pedidos
        """
        user = self.request.user
        
        # Staff y admin ven todos
        if user.role in ['STAFF', 'ADMIN'] or user.is_staff:
            return self.queryset
        
        # Clientes solo sus pedidos
        return self.queryset.filter(customer=user)

    def perform_create(self, serializer):
        """Asigna el usuario actual como customer al crear un pedido."""
        serializer.save(customer=self.request.user)

    @swagger_auto_schema(
        operation_description="Lista todos los pedidos (clientes solo ven los suyos)",
        manual_parameters=[
            openapi.Parameter('status', openapi.IN_QUERY, description="Filtrar por estado", type=openapi.TYPE_STRING),
            openapi.Parameter('priority', openapi.IN_QUERY, description="Filtrar por prioridad", type=openapi.TYPE_STRING),
            openapi.Parameter('order_type', openapi.IN_QUERY, description="Filtrar por tipo de pedido", type=openapi.TYPE_STRING),
            openapi.Parameter('search', openapi.IN_QUERY, description="Buscar en notas, mesa o cliente", type=openapi.TYPE_STRING),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Crea un nuevo pedido con items",
        request_body=OrderCreateSerializer
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Obtiene el detalle completo de un pedido con items"
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        method='patch',
        operation_description="Actualiza el estado de un pedido (solo staff/admin)",
        request_body=OrderStatusUpdateSerializer
    )
    @action(detail=True, methods=['patch'], permission_classes=[IsStaffOnly])
    def update_status(self, request, pk=None):
        """
        Endpoint personalizado para actualizar el estado del pedido.
        Valida transiciones permitidas y registra timestamps.
        
        RF-04: Seguimiento de estados
        """
        order = self.get_object()
        serializer = OrderStatusUpdateSerializer(data=request.data, context={'order': order})
        serializer.is_valid(raise_exception=True)
        
        new_status = serializer.validated_data['status']
        actual_time = serializer.validated_data.get('actual_time')
        
        order.status = new_status
        
        # Si se marca como completado, registrar timestamp
        if new_status == OrderStatus.DELIVERED and not order.completed_at:
            order.completed_at = timezone.now()
            if actual_time:
                order.actual_time = actual_time
        
        order.save()
        
        response_serializer = OrderSerializer(order)
        return Response(response_serializer.data)

    @swagger_auto_schema(
        method='get',
        operation_description="Obtiene pedidos activos (no completados ni cancelados)",
        manual_parameters=[
            openapi.Parameter('priority', openapi.IN_QUERY, description="Filtrar por prioridad", type=openapi.TYPE_STRING),
        ]
    )
    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Endpoint para obtener pedidos activos (en curso).
        RF-01: Visualización de pedidos en cocina.
        """
        active_statuses = [
            OrderStatus.PENDING,
            OrderStatus.CONFIRMED,
            OrderStatus.IN_PROGRESS,
            OrderStatus.READY
        ]
        queryset = self.get_queryset().filter(status__in=active_statuses)
        
        priority = request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        queryset = queryset.order_by('priority', 'created_at')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = OrderSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        method='get',
        operation_description="Obtiene pedidos completados del usuario",
        manual_parameters=[
            openapi.Parameter('limit', openapi.IN_QUERY, description="Número de pedidos a retornar", type=openapi.TYPE_INTEGER),
        ]
    )
    @action(detail=False, methods=['get'])
    def history(self, request):
        """
        Endpoint para obtener historial de pedidos completados.
        RF-04: Historial de pedidos del cliente.
        """
        completed_statuses = [OrderStatus.DELIVERED, OrderStatus.CANCELLED]
        queryset = self.get_queryset().filter(status__in=completed_statuses)
        
        limit = request.query_params.get('limit')
        if limit:
            try:
                queryset = queryset[:int(limit)]
            except ValueError:
                pass
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = OrderSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        method='post',
        operation_description="Cancela un pedido (solo si está en PENDING o CONFIRMED)"
    )
    @action(detail=True, methods=['post'], permission_classes=[IsOwnerOrStaff])
    def cancel(self, request, pk=None):
        """
        Endpoint para cancelar un pedido.
        Solo se puede cancelar si está en PENDING o CONFIRMED.
        
        RF-04: Cancelación de pedidos
        """
        order = self.get_object()
        
        if order.status not in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
            return Response(
                {'error': 'Solo se pueden cancelar pedidos pendientes o confirmados.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = OrderStatus.CANCELLED
        order.save()
        
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    @swagger_auto_schema(
        method='get',
        operation_description="Obtiene estadísticas de pedidos (solo staff/admin)"
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Endpoint para obtener estadísticas de pedidos.
        RF-06: Reportes y analytics.
        """
        # Solo staff/admin
        if request.user.role not in ['STAFF', 'ADMIN'] and not request.user.is_staff:
            return Response(
                {'error': 'No tienes permisos para ver estadísticas.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        queryset = self.get_queryset()
        
        stats = {
            'total_orders': queryset.count(),
            'by_status': {
                status_choice[0]: queryset.filter(status=status_choice[0]).count()
                for status_choice in OrderStatus.choices
            },
            'by_priority': {
                priority_choice[0]: queryset.filter(priority=priority_choice[0]).count()
                for priority_choice in OrderPriority.choices
            },
            'total_revenue': sum(order.total_amount for order in queryset),
            'average_order_value': (
                sum(order.total_amount for order in queryset) / queryset.count()
                if queryset.count() > 0 else 0
            )
        }
        
        return Response(stats)
