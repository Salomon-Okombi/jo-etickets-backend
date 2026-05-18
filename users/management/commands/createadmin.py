#users/management/commands/createadmin.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Créer un admin automatiquement"

    def handle(self, *args, **kwargs):
        User = get_user_model()

        username = "admin"
        email = "admin@test.com"
        password = "Admin123!"

        if not User.objects.filter(username=username).exists():
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )
            self.stdout.write(self.style.SUCCESS(" Admin créé"))
        else:
            self.stdout.write(self.style.WARNING(" Admin déjà existant"))