from django.db import models
from django.conf import settings

class Offre(models.Model):
    TYPE_OFFRE_CHOICES = [
        ('SOLO', 'Solo'),
        ('DUO', 'Duo'),
        ('FAMILIALE', 'Familiale'),
    ]
    STATUT_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('EPUISEE', 'Epuisée'),
        ('EXPIREE', 'Expirée'),
    ]

    evenement = models.ForeignKey(
        'evenements.Evenement',
        on_delete=models.CASCADE,
        related_name='offres'
    )
    createur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='offres_creees'
    )
    nom_offre = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    prix = models.DecimalField(max_digits=8, decimal_places=2)
    nb_personnes = models.PositiveIntegerField(default=1)
    type_offre = models.CharField(max_length=20, choices=TYPE_OFFRE_CHOICES)
    stock_total = models.PositiveIntegerField()
    stock_disponible = models.PositiveIntegerField()
    date_debut_vente = models.DateTimeField()
    date_fin_vente = models.DateTimeField()
    lieu_evenement = models.CharField(max_length=200, blank=True, null=True)
    discipline_sportive = models.CharField(max_length=100, blank=True, null=True)
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='ACTIVE'
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'offre'
        indexes = [
            models.Index(fields=['evenement', 'statut']),
        ]

    def __str__(self):
        return f"{self.nom_offre} ({self.evenement})"
