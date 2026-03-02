from django.db import models
from django.conf import settings


class Notification(models.Model):

    TYPE_CHOICES = [
        ("RESERVATION", "Réservation"),
        ("PAIEMENT", "Paiement"),
        ("OFFRE", "Offre"),
        ("SYSTEME", "Système"),
        ("RAPPEL", "Rappel"),
    ]

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    type_notification = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES
    )

    titre = models.CharField(max_length=255)
    message = models.TextField()

    # Lien optionnel vers une offre
    offre = models.ForeignKey(
        "offres.Offre",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications"
    )

    # Lien optionnel vers un événement
    evenement = models.ForeignKey(
        "evenements.Evenement",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications"
    )

    est_lue = models.BooleanField(default=False)

    date_creation = models.DateTimeField(auto_now_add=True)
    date_lecture = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "notification"
        ordering = ["-date_creation"]
        indexes = [
            models.Index(fields=["utilisateur", "est_lue"]),
        ]

    def __str__(self):
        return f"{self.titre} - {self.utilisateur}"