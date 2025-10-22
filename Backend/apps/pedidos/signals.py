"""
Señales de Pedidos
==================
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Order, OrderStatus


@receiver(post_save, sender=Order)
def handle_order_status_change(sender, instance, created, **kwargs):
    if created:
        print(f"Nuevo pedido creado: #{instance.id}")
    else:
        if instance.status == OrderStatus.CONFIRMED:
            print(f"Pedido #{instance.id} confirmado - descontar inventario")
        elif instance.status == OrderStatus.READY:
            print(f"Pedido #{instance.id} listo para entrega")
        elif instance.status == OrderStatus.DELIVERED:
            if not instance.completed_at:
                instance.completed_at = timezone.now()
                instance.save(update_fields=['completed_at'])
            print(f"Pedido #{instance.id} entregado")


@receiver(post_save, sender=Order)
def update_dish_popularity(sender, instance, created, **kwargs):
    if created:
        for item in instance.items.all():
            item.dish.popularity_score += 1
            item.dish.save(update_fields=['popularity_score'])
