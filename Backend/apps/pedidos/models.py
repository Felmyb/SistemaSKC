"""
Modelos de Pedidos
==================
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal


class OrderStatus(models.TextChoices):
    PENDING = 'PENDING', _('Pending')
    CONFIRMED = 'CONFIRMED', _('Confirmed')
    IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
    READY = 'READY', _('Ready')
    DELIVERED = 'DELIVERED', _('Delivered')
    CANCELLED = 'CANCELLED', _('Cancelled')


class OrderPriority(models.TextChoices):
    LOW = 'LOW', _('Low')
    MEDIUM = 'MEDIUM', _('Medium')
    HIGH = 'HIGH', _('High')
    URGENT = 'URGENT', _('Urgent')


class Order(models.Model):
    ORDER_TYPE_CHOICES = [
        ('DINE_IN', _('Dine In')),
        ('TAKEOUT', _('Takeout')),
        ('DELIVERY', _('Delivery')),
    ]

    customer = models.ForeignKey(
        'usuarios.User',
        on_delete=models.CASCADE,
        related_name='orders',
        help_text=_("Customer who placed the order (RF-04)")
    )

    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        help_text=_("Current order status (RF-01)")
    )

    priority = models.CharField(
        max_length=10,
        choices=OrderPriority.choices,
        default=OrderPriority.MEDIUM,
        help_text=_("Order priority for kitchen display (RF-01)")
    )

    order_type = models.CharField(
        max_length=10,
        choices=ORDER_TYPE_CHOICES,
        default='DINE_IN',
        help_text=_("Type of order")
    )

    table_number = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text=_("Table number for dine-in orders")
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text=_("Total order amount")
    )

    estimated_time = models.PositiveIntegerField(
        default=0,
        help_text=_("Estimated preparation time in minutes (RF-04)")
    )

    actual_time = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_("Actual preparation time in minutes (for analytics - RF-06)")
    )

    notes = models.TextField(
        blank=True,
        help_text=_("Special instructions or notes")
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("Order creation timestamp (traceability)")
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("Last update timestamp (RF-04)")
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Order completion timestamp (RF-06)")
    )

    class Meta:
        db_table = 'orders'
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['customer', 'created_at']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Order #{self.id} - {self.customer.username} ({self.status})"

    def get_priority_color(self):
        colors = {
            OrderPriority.LOW: '#4CAF50',
            OrderPriority.MEDIUM: '#FFC107',
            OrderPriority.HIGH: '#FF9800',
            OrderPriority.URGENT: '#F44336',
        }
        return colors.get(self.priority, '#9E9E9E')

    def calculate_total(self):
        total = sum(item.subtotal for item in self.items.all())
        self.total_amount = total
        self.save()
        return total


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        help_text=_("Parent order")
    )

    dish = models.ForeignKey(
        'platos.Dish',
        on_delete=models.PROTECT,
        related_name='order_items',
        help_text=_("Dish being ordered")
    )

    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text=_("Quantity ordered")
    )

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text=_("Price per unit at time of order")
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text=_("Calculated subtotal (quantity × unit_price)")
    )

    special_instructions = models.TextField(
        blank=True,
        help_text=_("Special instructions for this item")
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'order_items'
        verbose_name = _('Order Item')
        verbose_name_plural = _('Order Items')

    def __str__(self):
        return f"{self.quantity}× {self.dish.name}"

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)
