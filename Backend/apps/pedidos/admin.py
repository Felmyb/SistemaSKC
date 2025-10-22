"""
Admin de Pedidos
================
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ['dish', 'quantity', 'unit_price', 'subtotal', 'special_instructions']
    readonly_fields = ['subtotal']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'customer', 'status_colored', 'priority_colored', 'order_type',
        'table_number', 'total_amount', 'estimated_time', 'created_at'
    ]
    list_filter = ['status', 'priority', 'order_type', 'created_at']
    search_fields = ['id', 'customer__username', 'customer__email', 'table_number', 'notes']
    readonly_fields = ['created_at', 'updated_at', 'completed_at', 'priority_colored']

    fieldsets = (
        ('Información del Pedido', {
            'fields': ('customer', 'status', 'priority', 'priority_colored', 'order_type', 'table_number')
        }),
        ('Finanzas', {'fields': ('total_amount',)}),
        ('Tiempos (RF-04)', {
            'fields': ('estimated_time', 'actual_time', 'created_at', 'updated_at', 'completed_at')
        }),
        ('Información Adicional', {'fields': ('notes',)})
    )

    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    actions = ['mark_as_confirmed', 'mark_as_in_progress', 'mark_as_ready']

    def status_colored(self, obj):
        colors = {
            'PENDING': '#FFC107',
            'CONFIRMED': '#2196F3',
            'IN_PROGRESS': '#FF9800',
            'READY': '#4CAF50',
            'DELIVERED': '#8BC34A',
            'CANCELLED': '#F44336',
        }
        color = colors.get(obj.status, '#9E9E9E')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )

    status_colored.short_description = 'Estado'

    def priority_colored(self, obj):
        color = obj.get_priority_color()
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.get_priority_display()
        )

    priority_colored.short_description = 'Prioridad'

    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(status='CONFIRMED')
        self.message_user(request, f'{updated} pedidos marcados como confirmados.')

    mark_as_confirmed.short_description = "Marcar como Confirmado"

    def mark_as_in_progress(self, request, queryset):
        updated = queryset.update(status='IN_PROGRESS')
        self.message_user(request, f'{updated} pedidos marcados en progreso.')

    mark_as_in_progress.short_description = "Marcar como En Progreso"

    def mark_as_ready(self, request, queryset):
        updated = queryset.update(status='READY')
        self.message_user(request, f'{updated} pedidos marcados como listos.')

    mark_as_ready.short_description = "Marcar como Listo"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'dish', 'quantity', 'unit_price', 'subtotal', 'created_at']
    list_filter = ['created_at']
    search_fields = ['order__id', 'dish__name', 'special_instructions']
    readonly_fields = ['subtotal', 'created_at']
