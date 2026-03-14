from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


def generate_numero_commande():
    return f"CMD-{uuid.uuid4().hex[:10].upper()}"


class Commande(models.Model):
    STATUTS = [
        ("EN_ATTENTE", "En attente"),
        ("PAYEE", "Payée"),
        ("ANNULEE", "Annulée"),
    ]

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="commandes",
    )

    numero_commande = models.CharField(
        max_length=50,
        unique=True,
        default=generate_numero_commande,
        db_index=True,
    )

    statut = models.CharField(
        max_length=20,
        choices=STATUTS,
        default="EN_ATTENTE",
        db_index=True,
    )

    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    date_creation = models.DateTimeField(auto_now_add=True)
    date_paiement = models.DateTimeField(null=True, blank=True)

    reference_paiement = models.CharField(max_length=120, null=True, blank=True)

    class Meta:
        db_table = "commande"
        ordering = ["-date_creation"]

    def __str__(self):
        return f"{self.numero_commande} - {self.utilisateur_id} ({self.statut})"


class LigneCommande(models.Model):
    commande = models.ForeignKey(
        Commande,
        on_delete=models.CASCADE,
        related_name="lignes",
    )

    offre = models.ForeignKey(
        "offres.Offre",
        on_delete=models.PROTECT,
        related_name="lignes_commande",
    )

    quantite = models.PositiveIntegerField(default=1)

    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    sous_total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = "ligne_commande"

    def __str__(self):
        return f"{self.commande_id} - {self.offre_id} x{self.quantite}"