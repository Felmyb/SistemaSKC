"""
Orders Models
=============
Standard: IEEE 830
Requirements: RF-01, RF-04, RNF-01

Models for order management and tracking.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal


class OrderStatus(models.TextChoices):
    """
    Order status enumeration.
    
    Requirement: RF-01 - Order state management
    
    Design Thinking:
        - Empathize: Clear status for all stakeholders
        - Define: Well-defined order lifecycle
    """
    PENDING = 'PENDING', _('Pending')
    CONFIRMED = 'CONFIRMED', _('Confirmed')
    IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
    READY = 'READY', _('Ready')
    DELIVERED = 'DELIVERED', _('Delivered')
    CANCELLED = 'CANCELLED', _('Cancelled')


class OrderPriority(models.TextChoices):
    """
    Order priority levels.
    
    Requirement: RF-01 - Visual priority management
    
    Design Thinking:
        - Ideare: Color-coded priority system
        - Evaluate: Help cooks prioritize efficiently
    """
    LOW = 'LOW', _('Low')
    MEDIUM = 'MEDIUM', _('Medium')
    HIGH = 'HIGH', _('High')
    URGENT = 'URGENT', _('Urgent')


class Order(models.Model):
    """
    Order Model.
    
    Requirements:
        - RF-01: Digital order panel with priority
        - RF-04: Order tracking for customers
        - RNF-01: Efficient query performance
    
    Design Thinking:
        - Empathize: Customers want visibility, cooks need clarity
        - Prototype: Flexible model for various order types
        - Evaluate: Track metrics for continuous improvement
    
    Attributes:
        customer: User who placed the order
        status: Current order status
        priority: Order priority level
        table_number: Table number (for dine-in)
        order_type: Dine-in, takeout, or delivery
        total_amount: Total order cost
        estimated_time: Estimated preparation time (minutes)
        actual_time: Actual completion time (minutes)
        notes: Special instructions
        created_at: Order creation timestamp
        updated_at: Last update timestamp
    """
    
    ORDER_TYPE_CHOICES = [
        ('DINE_IN', _('Dine In')),
        ('TAKEOUT', _('Takeout')),
        ('DELIVERY', _('Delivery')),
    ]
    
    customer = models.ForeignKey(
        'users.User',
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
        """String representation."""
        return f"Order #{self.id} - {self.customer.username} ({self.status})"
    
    def get_priority_color(self):
        """
        Get color code for priority display.
        
        Returns:
            str: Hex color code
        
        Requirement: RF-01 - Visual priority system
        
        Design Thinking:
            - Ideare: Color coding for quick recognition
        """
        colors = {
            OrderPriority.LOW: '#4CAF50',      # Green
            OrderPriority.MEDIUM: '#FFC107',   # Amber
            OrderPriority.HIGH: '#FF9800',     # Orange
            OrderPriority.URGENT: '#F44336',   # Red
        }
        return colors.get(self.priority, '#9E9E9E')
    
    def calculate_total(self):
        """
        Calculate total from order items.
        
        Requirement: RF-02 - Automatic calculations
        
        Design Thinking:
            - Prototype: Automated calculations reduce errors
        """
        total = sum(item.subtotal for item in self.items.all())
        self.total_amount = total
        self.save()
        return total


class OrderItem(models.Model):
    """
    Order Item Model.
    
    Requirements:
        - RF-01: Detailed order information
        - RF-02: Inventory tracking per item
    
    Design Thinking:
        - Define: Clear item-level tracking
        - Evaluate: Support for customization and special requests
    
    Attributes:
        order: Parent order
        dish: Dish being ordered
        quantity: Number of items
        unit_price: Price per unit at time of order
        subtotal: Calculated subtotal
        special_instructions: Item-specific notes
    """
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        help_text=_("Parent order")
    )
    
    dish = models.ForeignKey(
        'dishes.Dish',
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
        """String representation."""
        return f"{self.quantity}× {self.dish.name}"
    
    def save(self, *args, **kwargs):
        """
        Override save to calculate subtotal.
        
        Requirement: RF-02 - Automatic calculations
        """
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)
