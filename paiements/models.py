from django.db import models
from django.conf import settings
from decimal import Decimal
import uuid


def generate_reference():
    return f"PAY-{uuid.uuid4().hex[:12].upper()}"


class Paiement(models.Model):
    STATUTS = [
        ("INITIE", "Initié"),
        ("SUCCES", "Succès"),
        ("ECHEC", "Échec"),
        ("ANNULE", "Annulé"),
    ]

    PROVIDERS = [
        ("MOCK", "Mock"),
        ("STRIPE", "Stripe"),
        ("PAYPAL", "Paypal"),
    ]

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="paiements",
    )

    commande = models.ForeignKey(
        "commandes.Commande",
        on_delete=models.CASCADE,
        related_name="paiements",
    )

    montant = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    statut = models.CharField(max_length=20, choices=STATUTS, default="INITIE", db_index=True)
    provider = models.CharField(max_length=20, choices=PROVIDERS, default="MOCK", db_index=True)

    reference = models.CharField(max_length=50, unique=True, default=generate_reference, db_index=True)

    date_creation = models.DateTimeField(auto_now_add=True)
    date_confirmation = models.DateTimeField(null=True, blank=True)

    raw_payload = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = "paiement"
        ordering = ["-date_creation"]

    def __str__(self):
        return f"{self.reference} - CMD#{self.commande_id} ({self.statut})"