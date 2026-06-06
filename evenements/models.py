# Last edited by you@example.com @ 05/06/26 19:24.
#evenements/view.py
from django.db import models
from decimal import Decimal
from django.utils import timezone


class Evenement(models.Model):
    """
    Modèle Evenement
    Utilisé pour :
    - la boutique publique
    - le back-office admin
    - l’API REST
    """

    STATUT_CHOICES = [
        ("BROUILLON", "Brouillon"),
        ("PUBLIE", "Publié"),
        ("ARCHIVE", "Archivé"),
    ]

    # =========================
    # Informations principales
    # =========================

    nom_evenement = models.CharField(
        max_length=255,
        verbose_name="Nom de l'événement"
    )

    discipline = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Discipline sportive"
    )

    lieu = models.CharField(
        max_length=255,
        verbose_name="Lieu"
    )

    # PÉRIODE DE L'ÉVÉNEMENT
    date_debut = models.DateTimeField(
        verbose_name="Date et heure de début de l'événement"
    )

    date_fin = models.DateTimeField(
        verbose_name="Date et heure de fin de l'événement"
    )

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default="BROUILLON",
        verbose_name="Statut"
    )

    prix_base = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Prix de base",
        help_text="Prix de base SOLO. DUO/FAMILLE = multiplicateur."
    )

    # =========================
    # Contenu boutique
    # =========================

    description_courte = models.TextField(
        blank=True,
        verbose_name="Description courte",
        help_text="Affichée sur la carte boutique"
    )

    description_longue = models.TextField(
        blank=True,
        verbose_name="Description longue",
        help_text="Affichée sur la page détail"
    )

    image = models.ImageField(
        upload_to="evenements/",
        blank=True,
        null=True,
        verbose_name="Image de l'événement"
    )

    # =========================
    # Système
    # =========================

    date_creation = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )

    # =========================
    # Meta & helpers
    # =========================

    class Meta:
        verbose_name = "Événement"
        verbose_name_plural = "Événements"
        ordering = ["date_debut"]

    def __str__(self) -> str:
        return self.nom_evenement

    @property
    def est_actif(self) -> bool:
        now = timezone.now()
        return (
            self.statut == "PUBLIE"
            and self.date_debut <= now <= self.date_fin
        )

    @property
    def est_expire(self) -> bool:
        return timezone.now() > self.date_fin