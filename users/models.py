# users/models.py
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class Utilisateur(AbstractUser):
    """
    Modèle personnalisé d'utilisateur.
    Étend AbstractUser pour ajouter des champs spécifiques à la plateforme.
    """

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

    cle_utilisateur = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="Clé unique d'identification interne de l'utilisateur."
    )
    type_compte = models.CharField(
        max_length=20,
        choices=TYPE_COMPTE_CHOICES,
        default='CLIENT',
        help_text="Type de compte utilisateur (Client, Admin ou Validateur)."
    )
    date_creation = models.DateTimeField(
        default=timezone.now,
        help_text="Date de création du compte utilisateur."
    )
    derniere_connexion = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Dernière connexion réussie de l'utilisateur."
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='ACTIF',
        help_text="Statut actuel du compte (actif, inactif ou suspendu)."
    )
    tentatives_connexion = models.IntegerField(
        default=0,
        help_text="Nombre de tentatives de connexion récentes (anti-brute-force)."
    )
    token_reset_mdp = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Token temporaire pour la réinitialisation du mot de passe."
    )
    date_token_reset = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date de génération du token de réinitialisation."
    )

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        db_table = 'utilisateur'
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["type_compte", "statut"]),
            models.Index(fields=["date_creation"]),
        ]
        ordering = ['-date_creation']
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return f"{self.username} ({self.type_compte}) - {self.statut}"

    def est_actif(self):
        """Retourne True si le compte est actif et non suspendu."""
        return self.statut == 'ACTIF'


class HistoriqueConnexion(models.Model):
    """
    Journal des connexions des utilisateurs (succès, échecs, blocages...).
    Permet de tracer toute l’activité liée à l’authentification.
    """

    STATUT_CONNEXION_CHOICES = [
        ('SUCCES', 'Succès'),
        ('ECHEC', 'Échec'),
        ('BLOQUE', 'Bloqué'),
    ]

    TYPE_ACTION_CHOICES = [
        ('CONNEXION', 'Connexion'),
        ('DECONNEXION', 'Déconnexion'),
        ('TENTATIVE', 'Tentative'),
    ]

    utilisateur = models.ForeignKey(
        'users.Utilisateur',
        on_delete=models.CASCADE,
        related_name='historique_connexions'
    )
    date_connexion = models.DateTimeField(auto_now_add=True)
    adresse_ip = models.CharField(
        max_length=45,
        null=True,
        blank=True,
        help_text="Adresse IP de la tentative de connexion."
    )
    user_agent = models.TextField(
        null=True,
        blank=True,
        help_text="Informations sur le navigateur ou l'appareil utilisé."
    )
    statut_connexion = models.CharField(
        max_length=20,
        choices=STATUT_CONNEXION_CHOICES,
        help_text="Résultat de la tentative (succès, échec, bloqué)."
    )
    type_action = models.CharField(
        max_length=20,
        choices=TYPE_ACTION_CHOICES,
        help_text="Type d'action enregistrée (connexion, déconnexion, tentative)."
    )

    class Meta:
        db_table = 'historique_connexion'
        indexes = [
            models.Index(fields=['utilisateur', 'date_connexion']),
            models.Index(fields=['statut_connexion']),
        ]
        ordering = ['-date_connexion']
        verbose_name = "Historique de connexion"
        verbose_name_plural = "Historiques de connexion"

    def __str__(self):
        return f"{self.utilisateur.username} - {self.date_connexion.strftime('%d/%m/%Y %H:%M')} - {self.statut_connexion}"
