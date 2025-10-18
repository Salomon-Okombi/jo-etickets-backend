# users/apps.py
from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        """
        Charge automatiquement les signaux de l'application Users.
        Cela permet de suivre les connexions et de mettre à jour la dernière connexion des utilisateurs.
        """
        import users.signals  # noqa: F401
