"""
accounts.apps
~~~~~~~~~~~~~

Defines the application configuration for the accounts app.
"""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """
    App configuration for the accounts application.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        """
        Import signals to ensure they are registered when the app is ready.
        """
        import accounts.signals
