from django.db import models
from django.conf import settings
from decimal import Decimal


class Panier(models.Model):
    STATUT_CHOICES = [
        ('ACTIF', 'Actif'),
        ('VALIDE', 'Valide'),
        ('ABANDONNE', 'Abandonné'),
        ('EXPIRE', 'Expiré'),
    ]

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='paniers'
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='ACTIF')
    montant_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    date_expiration = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'panier'
        ordering = ['-date_creation']

    def recalc_montant(self):
        """Recalcule le montant total du panier en fonction des lignes."""
        total = sum(ligne.sous_total for ligne in self.lignes.all()) if hasattr(self, 'lignes') else Decimal('0.00')
        self.montant_total = total
        self.save(update_fields=['montant_total'])
        return self.montant_total

    def __str__(self):
        return f"Panier #{self.pk} - {self.utilisateur}"


class LignePanier(models.Model):
    panier = models.ForeignKey(
        Panier,
        on_delete=models.CASCADE,
        related_name='lignes'
    )
    offre = models.ForeignKey(
        'offres.Offre',
        on_delete=models.CASCADE
    )
    quantite = models.PositiveIntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    sous_total = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=Decimal('0.00'))
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ligne_panier'
        indexes = [
            models.Index(fields=['panier']),
        ]
        unique_together = ('panier', 'offre')

    def save(self, *args, **kwargs):
        # Récupère le prix depuis l'offre si non défini
        if self.prix_unitaire is None:
            self.prix_unitaire = self.offre.prix

        # Calcul du sous-total
        self.sous_total = self.prix_unitaire * self.quantite
        super().save(*args, **kwargs)

        # Recalcule le montant du panier
        if self.panier_id:
            self.panier.recalc_montant()

    def __str__(self):
        return f"{self.quantite} x {self.offre.nom_offre} (Panier {self.panier.pk})"
