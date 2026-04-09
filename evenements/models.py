from django.db import models


class Evenement(models.Model):
    """
    Modèle Evenement
    Utilisé pour :
    - la boutique publique (frontend)
    - le back‑office admin
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

    date_evenement = models.DateField(
        verbose_name="Date de l'événement"
    )

    heure_evenement = models.TimeField(
        blank=True,
        null=True,
        verbose_name="Heure de l'événement"
    )

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default="BROUILLON",
        verbose_name="Statut"
    )

    # =========================
    # Contenu boutique
    # =========================

    description_courte = models.TextField(
        blank=True,
        help_text="Description affichée sur la carte de la boutique",
        verbose_name="Description courte"
    )

    description_longue = models.TextField(
        blank=True,
        help_text="Description affichée sur la page détail",
        verbose_name="Description longue"
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
        ordering = ["date_evenement"]

    def __str__(self) -> str:
        return self.nom_evenement

    @property
    def image_url(self):
        """
         Retourne l’URL réelle de l’image si elle existe
         Retourne None sinon

        IMPORTANT :
        - Aucun fallback ici
        - Le fallback visuel est géré côté frontend
        """
        if self.image:
            return self.image.url
        return None