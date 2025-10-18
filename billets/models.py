# billets/models.py
from django.db import models
from django.conf import settings
import uuid, qrcode, io, base64


# ---------- Générateurs utilitaires ----------
def generate_uuid():
    return str(uuid.uuid4())


def generate_numero_billet():
    """Génère un numéro unique et lisible pour le billet."""
    return f"EBILLET-{uuid.uuid4().hex[:10].upper()}"


def generate_cle_achat():
    """Clé interne de suivi d'achat (UUID)."""
    return str(uuid.uuid4())


# ---------- Modèle principal ----------
class EBillet(models.Model):
    """
    Représente un e-billet individuel, lié à une offre et un utilisateur.
    Chaque billet possède un QR code unique encodé en base64.
    """

    STATUTS = [
        ('VALIDE', 'Valide'),
        ('UTILISE', 'Utilisé'),
        ('ANNULE', 'Annulé'),
        ('EXPIRE', 'Expiré'),
    ]

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ebillets',
        help_text="Utilisateur propriétaire du billet."
    )

    offre = models.ForeignKey(
        'offres.Offre',
        on_delete=models.CASCADE,
        related_name='ebillets',
        help_text="Offre ou pack lié à ce billet."
    )

    validateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='billets_valides',
        help_text="Utilisateur (valideur) ayant scanné ou validé le billet."
    )

    numero_billet = models.CharField(
        max_length=50,
        unique=True,
        default=generate_numero_billet,
        help_text="Numéro public unique du billet."
    )

    date_achat = models.DateTimeField(
        auto_now_add=True,
        help_text="Date et heure d'achat du billet."
    )

    cle_achat = models.CharField(
        max_length=255,
        default=generate_cle_achat,
        help_text="Identifiant interne d'achat (UUID)."
    )

    cle_finale = models.CharField(
        max_length=512,
        default=generate_uuid,
        unique=True,
        editable=False,
        db_index=True,
        help_text="Clé finale utilisée pour le QR code et la validation."
    )

    qr_code = models.TextField(
        blank=True,
        help_text="Image du QR code encodée en base64."
    )

    prix_paye = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Prix payé pour ce billet."
    )

    statut = models.CharField(
        max_length=20,
        choices=STATUTS,
        default='VALIDE',
        db_index=True,
        help_text="Statut actuel du billet."
    )

    date_utilisation = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Date et heure de validation/utilisation du billet."
    )

    lieu_utilisation = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text="Lieu où le billet a été validé (ex: Entrée A)."
    )

    class Meta:
        db_table = 'e_billet'
        indexes = [
            models.Index(fields=['numero_billet']),
            models.Index(fields=['cle_finale']),
            models.Index(fields=['statut']),
            models.Index(fields=['date_utilisation']),
        ]
        ordering = ['-date_achat']
        verbose_name = "E-Billet"
        verbose_name_plural = "E-Billets"

    def save(self, *args, **kwargs):
        """
        Génère automatiquement le QR code et la clé finale lors de la création.
        """
        # Générer la clé finale avant le QR si elle n'existe pas
        if not self.cle_finale:
            self.cle_finale = generate_uuid()

        # Générer le QR code une seule fois
        if not self.qr_code and self.cle_finale:
            qr = qrcode.make(self.cle_finale)
            buffer = io.BytesIO()
            qr.save(buffer, format='PNG')
            self.qr_code = base64.b64encode(buffer.getvalue()).decode('ascii')

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.numero_billet} - {self.utilisateur.username} ({self.statut})"
