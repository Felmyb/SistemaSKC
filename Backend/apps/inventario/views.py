from decimal import Decimal
from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Ingredient, InventoryStock, InventoryTransaction
from .serializers import (
    IngredientSerializer,
    InventoryStockSerializer,
    InventoryTransactionSerializer,
    InventoryAdjustmentSerializer,
)
from .permissions import IsStaffOnly


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAuthenticated, IsStaffOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'unit', 'is_active']
    search_fields = ['name', 'supplier', 'description']
    ordering_fields = ['name', 'created_at', 'updated_at']

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """List ingredients below minimum stock threshold."""
        items = [i for i in self.get_queryset() if i.is_low_stock()]
        page = self.paginate_queryset(items)
        serializer = self.get_serializer(page or items, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        ingredient = self.get_object()
        ingredient.is_active = not ingredient.is_active
        ingredient.save(update_fields=['is_active'])
        return Response({'id': ingredient.id, 'is_active': ingredient.is_active})


class InventoryStockViewSet(viewsets.ModelViewSet):
    queryset = InventoryStock.objects.select_related('ingredient').all()
    serializer_class = InventoryStockSerializer
    permission_classes = [IsAuthenticated, IsStaffOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['ingredient', 'expiration_date']
    ordering_fields = ['updated_at', 'expiration_date']
    http_method_names = ['get', 'patch', 'post', 'head', 'options']

    @action(detail=True, methods=['post'])
    def adjust(self, request, pk=None):
        stock = self.get_object()
        serializer = InventoryAdjustmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        ttype = data['transaction_type']
        qty: Decimal = data['quantity']
        notes = data.get('notes', '')

        # Normalize sign: RESTOCK positive, WASTE/RETURN negative, ADJUSTMENT as provided
        delta = qty
        if ttype == 'RESTOCK':
            delta = qty
        elif ttype in ('WASTE', 'RETURN'):
            delta = -qty

        new_qty = stock.quantity + delta
        if new_qty < 0:
            return Response({'detail': 'Insufficient stock for this adjustment.'}, status=status.HTTP_400_BAD_REQUEST)

        stock.quantity = new_qty
        # Update restock timestamp if applicable
        if ttype == 'RESTOCK':
            stock.last_restocked = timezone.now()
        stock.save()

        InventoryTransaction.objects.create(
            ingredient=stock.ingredient,
            transaction_type=ttype,
            quantity=delta,
            balance_after=stock.quantity,
            notes=notes,
            user=request.user,
        )

        return Response(self.get_serializer(stock).data, status=status.HTTP_200_OK)


class InventoryTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InventoryTransaction.objects.select_related('ingredient', 'user').all()
    serializer_class = InventoryTransactionSerializer
    permission_classes = [IsAuthenticated, IsStaffOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['ingredient', 'transaction_type']
    ordering_fields = ['created_at']
