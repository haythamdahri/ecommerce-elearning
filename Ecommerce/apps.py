from django.apps import AppConfig


class EcommerceConfig(AppConfig):
    name = 'Ecommerce'

    def ready(self):
        import Ecommerce.signals