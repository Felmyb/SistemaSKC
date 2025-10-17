"""
Dishes Models
=============
Standard: IEEE 830
Requirements: RF-01, RF-02

Models for menu dishes and recipes.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal


class DishCategory(models.TextChoices):
    """
    Dish category enumeration.
    
    Requirement: RF-01 - Menu organization
    
    Design Thinking:
        - Ideare: Intuitive menu categories
    """
    APPETIZER = 'APPETIZER', _('Appetizer')
    SOUP = 'SOUP', _('Soup')
    SALAD = 'SALAD', _('Salad')
    MAIN_COURSE = 'MAIN_COURSE', _('Main Course')
    SIDE_DISH = 'SIDE_DISH', _('Side Dish')
    DESSERT = 'DESSERT', _('Dessert')
    BEVERAGE = 'BEVERAGE', _('Beverage')
    SPECIAL = 'SPECIAL', _('Special')


class Dish(models.Model):
    """
    Dish Model.
    
    Requirements:
        - RF-01: Menu management
        - RF-02: Recipe for inventory tracking
        - RNF-06: Accessible menu information
    
    Design Thinking:
        - Empathize: Customers want detailed dish info
        - Ideare: Rich menu presentation
        - Evaluate: Popular dishes tracking
    
    Attributes:
        name: Dish name
        description: Dish description
        category: Dish category
        price: Selling price
        preparation_time: Average preparation time
        image: Dish image
        is_available: Availability status
        is_vegetarian: Vegetarian flag
        is_vegan: Vegan flag
        allergens: Allergen information
    """
    
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text=_("Dish name")
    )
    
    description = models.TextField(
        help_text=_("Dish description (RNF-06 - Accessibility)")
    )
    
    category = models.CharField(
        max_length=20,
        choices=DishCategory.choices,
        default=DishCategory.MAIN_COURSE,
        help_text=_("Dish category (RF-01)")
    )
    
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text=_("Selling price")
    )
    
    preparation_time = models.PositiveIntegerField(
        default=15,
        help_text=_("Average preparation time in minutes (RF-01, RF-04)")
    )
    
    image = models.ImageField(
        upload_to='dishes/',
        blank=True,
        null=True,
        help_text=_("Dish image")
    )
    
    is_available = models.BooleanField(
        default=True,
        help_text=_("Is this dish currently available? (RF-01)")
    )
    
    is_vegetarian = models.BooleanField(
        default=False,
        help_text=_("Is this dish vegetarian?")
    )
    
    is_vegan = models.BooleanField(
        default=False,
        help_text=_("Is this dish vegan?")
    )
    
    allergens = models.TextField(
        blank=True,
        help_text=_("Allergen information (RNF-06 - Safety)")
    )
    
    popularity_score = models.IntegerField(
        default=0,
        help_text=_("Popularity score for recommendations (RF-03, RF-06)")
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'dishes'
        verbose_name = _('Dish')
        verbose_name_plural = _('Dishes')
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['category', 'is_available']),
            models.Index(fields=['-popularity_score']),
        ]
    
    def __str__(self):
        """String representation."""
        return f"{self.name} ({self.get_category_display()})"
    
    def check_availability(self):
        """
        Check if dish can be prepared based on ingredient availability.
        
        Returns:
            bool: True if all ingredients are available
        
        Requirement: RF-02 - Inventory integration
        
        Design Thinking:
            - Prototype: Automatic availability checking
            - Evaluate: Prevent orders for unavailable dishes
        """
        for recipe_item in self.recipe_items.all():
            if not recipe_item.check_availability():
                return False
        return True
    
    def calculate_cost(self):
        """
        Calculate dish cost based on ingredients.
        
        Returns:
            Decimal: Total ingredient cost
        
        Requirement: RF-06 - Cost analysis
        """
        total_cost = sum(
            item.ingredient.cost_per_unit * item.quantity
            for item in self.recipe_items.all()
        )
        return total_cost


class RecipeItem(models.Model):
    """
    Recipe Item Model (Ingredients in a dish).
    
    Requirements:
        - RF-02: Recipe-based inventory deduction
        - RF-06: Cost calculation
    
    Design Thinking:
        - Define: Clear ingredient requirements per dish
        - Prototype: Automated inventory tracking
    
    Attributes:
        dish: Related dish
        ingredient: Required ingredient
        quantity: Quantity needed
        notes: Preparation notes
    """
    
    dish = models.ForeignKey(
        Dish,
        on_delete=models.CASCADE,
        related_name='recipe_items',
        help_text=_("Related dish")
    )
    
    ingredient = models.ForeignKey(
        'inventory.Ingredient',
        on_delete=models.PROTECT,
        related_name='recipe_items',
        help_text=_("Required ingredient (RF-02)")
    )
    
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text=_("Quantity needed per serving (RF-02)")
    )
    
    notes = models.TextField(
        blank=True,
        help_text=_("Preparation notes or special instructions")
    )
    
    class Meta:
        db_table = 'recipe_items'
        verbose_name = _('Recipe Item')
        verbose_name_plural = _('Recipe Items')
        unique_together = ['dish', 'ingredient']
    
    def __str__(self):
        """String representation."""
        return f"{self.dish.name} - {self.ingredient.name}: {self.quantity}"
    
    def check_availability(self):
        """
        Check if enough ingredient is in stock.
        
        Returns:
            bool: True if sufficient stock
        
        Requirement: RF-02 - Stock verification
        """
        try:
            return self.ingredient.stock.quantity >= self.quantity
        except AttributeError:
            return False
