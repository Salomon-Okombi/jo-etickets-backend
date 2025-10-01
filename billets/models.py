from django.db import models
from django.conf import settings
import uuid
import qrcode, io, base64

# ---------- Générateurs utilitaires ----------
def generate_uuid():
    return str(uuid.uuid4())

def generate_numero_billet():
    return f"EBILLET-{uuid.uuid4().hex[:10].upper()}"

def generate_cle_achat():
    return str(uuid.uuid4())


# ---------- Modèle ----------
class EBillet(models.Model):
    STATUTS = [
        ('VALIDE', 'Valide'),
        ('UTILISE', 'Utilisé'),
        ('ANNULE', 'Annulé'),
        ('EXPIRE', 'Expiré'),
    ]

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ebillets'
    )
    offre = models.ForeignKey(
        'offres.Offre',
        on_delete=models.CASCADE,
        related_name='ebillets'
    )
    id_validateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='billets_valides'
    )
    numero_billet = models.CharField(
        max_length=50,
        unique=True,
        default=generate_numero_billet
    )
    date_achat = models.DateTimeField(auto_now_add=True)
    cle_achat = models.CharField(
        max_length=255,
        default=generate_cle_achat
    )
    cle_finale = models.CharField(
        max_length=512,
        default=generate_uuid,
        editable=False
    )
    qr_code = models.TextField(blank=True)  # PNG encodé en base64
    prix_paye = models.DecimalField(max_digits=8, decimal_places=2)
    statut = models.CharField(max_length=20, choices=STATUTS, default='VALIDE')
    date_utilisation = models.DateTimeField(null=True, blank=True)
    lieu_utilisation = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = 'e_billet'
        indexes = [
            models.Index(fields=['numero_billet']),
        ]

    def save(self, *args, **kwargs):
        # Générer la clé finale si absente
        if not self.cle_finale:
            user_cle = str(self.utilisateur.cle_utilisateur)
            achat_cle = str(self.cle_achat)
            self.cle_finale = f"{user_cle}-{achat_cle}"

        # Générer le QR code si absent
        if not self.qr_code:
            qr = qrcode.make(self.cle_finale)
            buffer = io.BytesIO()
            qr.save(buffer, format='PNG')
            self.qr_code = base64.b64encode(buffer.getvalue()).decode('ascii')

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.numero_billet} - {self.utilisateur}"
