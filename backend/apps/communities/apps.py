from django.apps import AppConfig


class CommunitiesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.communities"

    def ready(self):
        """Import signals when app is ready."""
        import apps.communities.signals  # noqa: F401
