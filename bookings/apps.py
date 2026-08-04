from django.apps import AppConfig


class BookingsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bookings"

    def ready(self):
        # Register deploy-time security checks (SECRET_KEY / PII / webhook secret).
        from core import checks  # noqa: F401
