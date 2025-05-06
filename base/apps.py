from django.apps import AppConfig
from django.db.utils import ProgrammingError, IntegrityError


class BaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'base'
    def ready(self):
        import base.signals
        try:
            from django.contrib.sites.models import Site
            # Delete any duplicate domains first
            Site.objects.filter(domain='mindbridge-production-c67d.up.railway.app').exclude(id=1).delete()
            # Create our preferred site
            Site.objects.update_or_create(
                id=1,
                defaults={
                    'domain': 'mindbridge-production-c67d.up.railway.app',
                    'name': 'MindBridge'
                }
            )
        except (ProgrammingError, IntegrityError):
            # Skip during initial migrations or if table doesn't exist yet
            pass
        except Exception as e:
            print(f"Sites setup error: {e}")