from django.utils import timezone

from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class Utilisateur(AbstractUser):
    TYPE_COMPTE_CHOICES = [
        ('CLIENT', 'Client'),
        ('ADMIN', 'Admin'),
        ('VALIDATEUR', 'Validateur'),
    ]

    STATUT_CHOICES = [
        ('ACTIF', 'Actif'),
        ('INACTIF', 'Inactif'),
        ('SUSPENDU', 'Suspendu'),
    ]

    cle_utilisateur = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    type_compte = models.CharField(max_length=20, choices=TYPE_COMPTE_CHOICES, default='ADMIN')
    date_creation = models.DateTimeField(default=timezone.now)
    derniere_connexion = models.DateTimeField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='ACTIF')
    tentatives_connexion = models.IntegerField(default=0)
    token_reset_mdp = models.CharField(max_length=255, null=True, blank=True)
    date_token_reset = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'utilisateur'

    def __str__(self):
        return self.username


class HistoriqueConnexion(models.Model):
    STATUT_CONNEXION_CHOICES = [
        ('SUCCES', 'Succes'),
        ('ECHEC', 'Echec'),
        ('BLOQUE', 'Bloque'),
    ]
    TYPE_ACTION_CHOICES = [
        ('CONNEXION', 'Connexion'),
        ('DECONNEXION', 'Deconnexion'),
        ('TENTATIVE', 'Tentative'),
    ]

    utilisateur = models.ForeignKey('users.Utilisateur', on_delete=models.CASCADE, related_name='historique_connexions')
    date_connexion = models.DateTimeField(auto_now_add=True)
    adresse_ip = models.CharField(max_length=45, null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    statut_connexion = models.CharField(max_length=20, choices=STATUT_CONNEXION_CHOICES)
    type_action = models.CharField(max_length=20, choices=TYPE_ACTION_CHOICES)

    class Meta:
        db_table = 'historique_connexion'
        indexes = [
            models.Index(fields=['utilisateur', 'date_connexion']),
        ]

    def __str__(self):
        return f"{self.utilisateur} - {self.date_connexion} - {self.statut_connexion}"
