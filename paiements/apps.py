# paiements/apps.py
from django.apps import AppConfig


class PaiementsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'paiements'

    def ready(self):
        """
        Charge automatiquement les signaux de l'application Paiements.
        Cela permet de mettre à jour les statistiques dès qu'une commande est payée.
        """
        import paiements.signals  
