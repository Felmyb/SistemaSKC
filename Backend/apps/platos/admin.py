"""
Configuración del Admin para Platos
====================================
"""

from django.contrib import admin
from .models import Dish, RecipeItem


class RecipeItemInline(admin.TabularInline):
    """Inline para editar ingredientes de la receta."""
    model = RecipeItem
    extra = 1
    # autocomplete_fields = ['ingredient']  # Descomentar cuando Ingredient tenga admin registrado


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    """Admin para Dish con inlines de receta."""
    list_display = ['name', 'category', 'price', 'preparation_time', 'is_available', 'popularity_score', 'created_at']
    list_filter = ['category', 'is_available', 'is_vegetarian', 'is_vegan']
    search_fields = ['name', 'description', 'allergens']
    readonly_fields = ['popularity_score', 'created_at', 'updated_at']
    inlines = [RecipeItemInline]
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description', 'category', 'image')
        }),
        ('Precio y Tiempo', {
            'fields': ('price', 'preparation_time')
        }),
        ('Características', {
            'fields': ('is_available', 'is_vegetarian', 'is_vegan', 'allergens')
        }),
        ('Métricas', {
            'fields': ('popularity_score', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
