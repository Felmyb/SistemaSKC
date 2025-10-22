from django.apps import AppConfig


class PedidosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.pedidos'
    verbose_name = 'Gestión de Pedidos'

    def ready(self):
        try:
            import apps.pedidos.signals  # noqa
        except Exception:
            pass
