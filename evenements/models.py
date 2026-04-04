from django.db import models

class Evenement(models.Model):
    STATUT_CHOICES = [
        ("BROUILLON", "Brouillon"),
        ("PUBLIE", "Publié"),
        ("ARCHIVE", "Archivé"),
    ]

    nom_evenement = models.CharField(max_length=255)

    description_courte = models.TextField(
        help_text="Description affichée dans la boutique",
        blank=True
    )

    description_longue = models.TextField(
        help_text="Description affichée sur la page détail",
        blank=True
    )

    image = models.ImageField(
        upload_to="evenements/",
        blank=True,
        null=True
    )

    date_evenement = models.DateField()
    heure_evenement = models.TimeField(blank=True, null=True)
    lieu = models.CharField(max_length=255)
    discipline = models.CharField(max_length=255, blank=True)

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default="BROUILLON"
    )

    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date_evenement"]

    def __str__(self):
        return self.nom_evenement

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        return "/static/images/event-default.jpg"