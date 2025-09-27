# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class Utilisateur(AbstractUser):
    # Tu peux ajouter des champs personnalisés ici si tu veux
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.username
