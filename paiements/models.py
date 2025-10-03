from django.db import models
from django.conf import settings
import uuid
from paniers.models import Panier

def generate_numero_commande():
    """Génère un identifiant unique pour la commande."""
    return uuid.uuid4().hex.upper()[:16]

class Commande(models.Model):
    """Représente une commande passée par un utilisateur."""
    
    STATUT_PAIEMENT_CHOICES = [
        ('ATTENTE', 'Attente'),
        ('PAYE', 'Payé'),
        ('ECHOUE', 'Échoué'),
        ('REMBOURSE', 'Remboursé'),
    ]

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='commandes'
    )
    panier = models.OneToOneField(
        Panier,
        on_delete=models.CASCADE,
        related_name='commande'
    )
    numero_commande = models.CharField(
        max_length=50,
        unique=True,
        default=generate_numero_commande
    )
    date_commande = models.DateTimeField(auto_now_add=True)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    statut_paiement = models.CharField(
        max_length=20,
        choices=STATUT_PAIEMENT_CHOICES,
        default='ATTENTE'
    )
    methode_paiement = models.CharField(max_length=50, null=True, blank=True)
    reference_paiement = models.CharField(max_length=100, null=True, blank=True)
    date_paiement = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'commande'
        indexes = [
            models.Index(fields=['utilisateur', 'date_commande']),
        ]
        ordering = ['-date_commande']

    def __str__(self):
        return f"Commande {self.numero_commande} - {self.utilisateur}"
