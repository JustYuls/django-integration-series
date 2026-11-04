from django.apps import AppConfig
from django.db.models.signals import post_migrate


class AccountsConfig(AppConfig):
    name = "accounts"

    def ready(self):
        from .roles import create_roles

        # accounts has no models, so Django does not send it post_migrate: listen to everyone, act once (see roles.py)
        post_migrate.connect(create_roles, dispatch_uid="accounts.create_roles")
