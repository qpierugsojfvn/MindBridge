from django.apps import AppConfig


class MindbridgeAuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mindbridge_auth'

    def ready(self):
        import mindbridge_auth.signals
