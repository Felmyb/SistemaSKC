"""
Inventory Models
================
Standard: IEEE 830
Requirements: RF-02

Models for ingredient and inventory management.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal


class InventoryCategory(models.TextChoices):
    """
    Inventory category enumeration.
    
    Requirement: RF-02 - Organized inventory management
    
    Design Thinking:
        - Define: Logical categorization for better management
    """
    VEGETABLES = 'VEGETABLES', _('Vegetables')
    FRUITS = 'FRUITS', _('Fruits')
    MEAT = 'MEAT', _('Meat')
    SEAFOOD = 'SEAFOOD', _('Seafood')
    DAIRY = 'DAIRY', _('Dairy')
    GRAINS = 'GRAINS', _('Grains')
    SPICES = 'SPICES', _('Spices')
    BEVERAGES = 'BEVERAGES', _('Beverages')
    OTHER = 'OTHER', _('Other')


class UnitOfMeasure(models.TextChoices):
    """
    Unit of measure for ingredients.
    
    Requirement: RF-02 - Standardized measurements
    """
    KILOGRAM = 'KG', _('Kilogram')
    GRAM = 'G', _('Gram')
    LITER = 'L', _('Liter')
    MILLILITER = 'ML', _('Milliliter')
    PIECE = 'PC', _('Piece')
    DOZEN = 'DZ', _('Dozen')
    POUND = 'LB', _('Pound')
    OUNCE = 'OZ', _('Ounce')


class Ingredient(models.Model):
    """
    Ingredient Model.
    
    Requirements:
        - RF-02: Ingredient tracking
        - RF-03: Data for demand prediction
    
    Design Thinking:
        - Empathize: Inventory managers need clear ingredient info
        - Define: Standardized ingredient data structure
    
    Attributes:
        name: Ingredient name
        category: Ingredient category
        unit: Unit of measurement
        cost_per_unit: Cost per unit
        supplier: Supplier information
        minimum_stock: Minimum stock level (alert threshold)
        is_active: Active status
    """
    
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text=_("Ingredient name")
    )
    
    category = models.CharField(
        max_length=20,
        choices=InventoryCategory.choices,
        default=InventoryCategory.OTHER,
        help_text=_("Ingredient category (RF-02)")
    )
    
    unit = models.CharField(
        max_length=5,
        choices=UnitOfMeasure.choices,
        default=UnitOfMeasure.KILOGRAM,
        help_text=_("Unit of measurement")
    )
    
    cost_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text=_("Cost per unit (for analytics - RF-06)")
    )
    
    supplier = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("Primary supplier")
    )
    
    minimum_stock = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('10.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text=_("Minimum stock level for alerts (RF-02)")
    )
    
    description = models.TextField(
        blank=True,
        help_text=_("Additional information")
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text=_("Is this ingredient currently in use?")
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ingredients'
        verbose_name = _('Ingredient')
        verbose_name_plural = _('Ingredients')
        ordering = ['name']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        """String representation."""
        return f"{self.name} ({self.get_unit_display()})"
    
    @property
    def current_stock(self):
        """
        Get current stock level.
        
        Returns:
            Decimal: Current stock quantity
        
        Requirement: RF-02 - Real-time stock visibility
        """
        try:
            return self.stock.quantity
        except AttributeError:
            return Decimal('0.00')
    
    def is_low_stock(self):
        """
        Check if ingredient is low on stock.
        
        Returns:
            bool: True if stock is below minimum
        
        Requirement: RF-02 - Low stock detection
        """
        return self.current_stock < self.minimum_stock


class InventoryStock(models.Model):
    """
    Inventory Stock Model.
    
    Requirements:
        - RF-02: Real-time inventory tracking
        - RF-03: Historical data for predictions
    
    Design Thinking:
        - Prototype: Automatic stock updates
        - Evaluate: Track accuracy and alerts
    
    Attributes:
        ingredient: Related ingredient
        quantity: Current quantity in stock
        last_restocked: Last restock date
        expiration_date: Expiration date (if applicable)
    """
    
    ingredient = models.OneToOneField(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='stock',
        help_text=_("Related ingredient")
    )
    
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text=_("Current quantity in stock (RF-02)")
    )
    
    last_restocked = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Last restock date")
    )
    
    expiration_date = models.DateField(
        null=True,
        blank=True,
        help_text=_("Expiration date (if applicable)")
    )
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'inventory_stock'
        verbose_name = _('Inventory Stock')
        verbose_name_plural = _('Inventory Stocks')
    
    def __str__(self):
        """String representation."""
        return f"{self.ingredient.name}: {self.quantity} {self.ingredient.get_unit_display()}"
    
    def add_stock(self, quantity):
        """
        Add stock quantity.
        
        Args:
            quantity (Decimal): Quantity to add
        
        Requirement: RF-02 - Stock management
        """
        self.quantity += quantity
        self.save()
        
        # Log transaction
        InventoryTransaction.objects.create(
            ingredient=self.ingredient,
            transaction_type='RESTOCK',
            quantity=quantity,
            balance_after=self.quantity
        )
    
    def deduct_stock(self, quantity):
        """
        Deduct stock quantity.
        
        Args:
            quantity (Decimal): Quantity to deduct
        
        Returns:
            bool: True if successful, False if insufficient stock
        
        Requirement: RF-02 - Automatic deduction
        """
        if self.quantity >= quantity:
            self.quantity -= quantity
            self.save()
            
            # Log transaction
            InventoryTransaction.objects.create(
                ingredient=self.ingredient,
                transaction_type='USAGE',
                quantity=-quantity,
                balance_after=self.quantity
            )
            return True
        return False


class InventoryTransaction(models.Model):
    """
    Inventory Transaction Log.
    
    Requirements:
        - RF-02: Transaction tracking
        - RNF-04: Traceability
    
    Design Thinking:
        - Evaluate: Audit trail for inventory changes
        - Define: Clear transaction history
    
    Attributes:
        ingredient: Related ingredient
        transaction_type: Type of transaction
        quantity: Quantity changed (positive or negative)
        balance_after: Stock balance after transaction
        notes: Transaction notes
        user: User who performed transaction
    """
    
    TRANSACTION_TYPES = [
        ('RESTOCK', _('Restock')),
        ('USAGE', _('Usage (Order)')),
        ('ADJUSTMENT', _('Manual Adjustment')),
        ('WASTE', _('Waste/Spoilage')),
        ('RETURN', _('Return to Supplier')),
    ]
    
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='transactions',
        help_text=_("Related ingredient")
    )
    
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES,
        help_text=_("Type of transaction (RF-02)")
    )
    
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text=_("Quantity changed (positive for add, negative for deduct)")
    )
    
    balance_after = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text=_("Stock balance after transaction")
    )
    
    notes = models.TextField(
        blank=True,
        help_text=_("Transaction notes")
    )
    
    user = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='inventory_transactions',
        help_text=_("User who performed transaction (RNF-04)")
    )
    
    related_order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inventory_transactions',
        help_text=_("Related order (if applicable)")
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("Transaction timestamp (traceability)")
    )
    
    class Meta:
        db_table = 'inventory_transactions'
        verbose_name = _('Inventory Transaction')
        verbose_name_plural = _('Inventory Transactions')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['ingredient', 'created_at']),
            models.Index(fields=['transaction_type']),
        ]
    
    def __str__(self):
        """String representation."""
        return f"{self.ingredient.name} - {self.get_transaction_type_display()}: {self.quantity}"
