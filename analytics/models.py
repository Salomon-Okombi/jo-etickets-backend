# analytics/models.py
from decimal import Decimal
from django.db import models
from django.db.models import Q, CheckConstraint


class StatistiquesVente(models.Model):
    """
    Statistiques agrégées par offre.
    - Ces données sont MAJ automatiquement par les signaux de paiements.
    - Aucune écriture manuelle via l'API (voir ViewSet en read-only).
    """
    offre = models.OneToOneField(
        'offres.Offre',
        on_delete=models.CASCADE,
        related_name='statistiques'
    )
    nombre_ventes = models.IntegerField(default=0)
    chiffre_affaires = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    date_derniere_maj = models.DateTimeField(auto_now=True)

    # Optionnel (facultatif selon ce que vous calculez côté signal / batch)
    moyenne_ventes_jour = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("0.00"))
    pic_ventes_heure = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'statistiques_vente'
        indexes = [
            models.Index(fields=['offre']),
            models.Index(fields=['-date_derniere_maj']),
        ]
        constraints = [
            CheckConstraint(check=Q(nombre_ventes__gte=0), name="stats_nombre_ventes_non_negatif"),
            CheckConstraint(check=Q(chiffre_affaires__gte=0), name="stats_chiffre_affaires_non_negatif"),
            CheckConstraint(check=Q(moyenne_ventes_jour__gte=0), name="stats_moy_ventes_jour_non_negatif"),
        ]
        ordering = ['-date_derniere_maj']
        verbose_name = "Statistique de Vente"
        verbose_name_plural = "Statistiques de Ventes"

    def __str__(self):
        return f"Stats Offre {self.offre_id} - ventes: {self.nombre_ventes}"
