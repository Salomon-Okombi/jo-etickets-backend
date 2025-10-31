# paniers/models.py
from django.db import models
from django.conf import settings
from decimal import Decimal
from django.db.models import Q, UniqueConstraint, CheckConstraint, Sum, F, Value, DecimalField
from django.db.models.functions import Coalesce


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
        indexes = [
            models.Index(fields=['utilisateur', 'statut']),
        ]

    def recalc_montant(self):
        """
        Recalcule le montant total du panier en une seule requête.
        Utilise COALESCE pour éviter les None.
        """
        total = self.lignes.aggregate(
            total=Coalesce(Sum(F('prix_unitaire') * F('quantite'), output_field=DecimalField(max_digits=10, decimal_places=2)),
                           Value(Decimal('0.00')))
        )['total'] or Decimal('0.00')

        # Force 2 décimales pour éviter les surprises d’arrondi
        self.montant_total = Decimal(total).quantize(Decimal('0.00'))
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
        on_delete=models.CASCADE,
        null=False,  # on interdit les lignes orphelines par le schéma
        blank=False
    )
    quantite = models.PositiveIntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    sous_total = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=Decimal('0.00'))
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ligne_panier'
        indexes = [
            models.Index(fields=['panier']),
            models.Index(fields=['offre']),
        ]
        constraints = [
            # Unicité (une offre unique par panier)
            UniqueConstraint(fields=['panier', 'offre'], name='uniq_panier_offre'),
            # Interdit les lignes sans offre
            CheckConstraint(check=Q(offre__isnull=False), name='ligne_panier_offre_nn'),
            # Interdit quantite <= 0
            CheckConstraint(check=Q(quantite__gt=0), name='ligne_panier_quantite_gt_0'),
        ]

    def save(self, *args, **kwargs):
        # Définit le prix depuis l'offre si non fourni
        if self.prix_unitaire is None:
            # self.offre ne peut pas être None (FK not null + contrainte)
            self.prix_unitaire = self.offre.prix

        # Calcul du sous-total
        self.sous_total = (self.prix_unitaire * self.quantite).quantize(Decimal('0.00'))

        super().save(*args, **kwargs)

        # Recalcule le montant du panier (après save)
        if self.panier_id:
            self.panier.recalc_montant()

    def delete(self, *args, **kwargs):
        panier = self.panier  # garder la référence pour recalcul après suppression
        super().delete(*args, **kwargs)
        if panier and panier.pk:
            panier.recalc_montant()

    def __str__(self):
        return f"{self.quantite} x {self.offre.nom_offre} (Panier {self.panier.pk})"
