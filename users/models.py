#users/model.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class Utilisateur(AbstractUser):
    """
    Modèle utilisateur personnalisé pour l'application.
    """

    ROLE_CHOICES = [
        ("ADMIN", "Administrateur"),
        ("ORGANISATEUR", "Organisateur"),
        ("UTILISATEUR", "Utilisateur"),
    ]

    email = models.EmailField(unique=True)

    telephone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="UTILISATEUR"
    )

    photo_profil = models.ImageField(
        upload_to="users/profils/",
        blank=True,
        null=True
    )

    date_creation = models.DateTimeField(
        auto_now_add=True
    )

    derniere_modification = models.DateTimeField(
        auto_now=True
    )

    est_verifie = models.BooleanField(
        default=False,
        help_text="Indique si l'utilisateur a vérifié son email."
    )

    est_bloque = models.BooleanField(
        default=False,
        help_text="Indique si le compte est bloqué."
    )

    tentatives_connexion = models.IntegerField(
        default=0
    )

    derniere_connexion_ip = models.CharField(
        max_length=45,
        blank=True,
        null=True
    )

    class Meta:
        db_table = "utilisateurs"
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.username} ({self.email})"


class HistoriqueConnexion(models.Model):

    STATUT_CONNEXION_CHOICES = [
        ("SUCCES", "Succès"),
        ("ECHEC", "Échec"),
        ("BLOQUE", "Bloqué"),
    ]

    TYPE_ACTION_CHOICES = [
        ("CONNEXION", "Connexion"),
        ("DECONNEXION", "Déconnexion"),
        ("TENTATIVE", "Tentative"),
    ]

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="historique_connexions",
    )

    identifiant_saisi = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Identifiant saisi lors d'une tentative (username/email).",
    )

    date_connexion = models.DateTimeField(
        auto_now_add=True
    )

    adresse_ip = models.CharField(
        max_length=45,
        null=True,
        blank=True,
        help_text="Adresse IP de la tentative de connexion.",
    )

    user_agent = models.TextField(
        null=True,
        blank=True,
        help_text="Informations sur le navigateur ou l'appareil utilisé.",
    )

    statut_connexion = models.CharField(
        max_length=20,
        choices=STATUT_CONNEXION_CHOICES,
    )

    type_action = models.CharField(
        max_length=20,
        choices=TYPE_ACTION_CHOICES,
    )

    class Meta:
        db_table = "historique_connexion"
        indexes = [
            models.Index(fields=["utilisateur", "date_connexion"]),
            models.Index(fields=["statut_connexion"]),
        ]
        ordering = ["-date_connexion"]
        verbose_name = "Historique de connexion"
        verbose_name_plural = "Historiques de connexion"

    def __str__(self):
        identite = (
            self.utilisateur.username
            if self.utilisateur
            else (self.identifiant_saisi or "inconnu")
        )

        return f"{identite} - {self.date_connexion.strftime('%d/%m/%Y %H:%M')} - {self.statut_connexion}"