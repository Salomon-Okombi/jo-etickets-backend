from django.db import models
from django.conf import settings
import uuid
import qrcode
import io
import base64


# ---------- Générateurs utilitaires ----------

def generate_uuid():
    """
    Conservé pour compatibilité avec les anciennes migrations Django.
    Ne doit plus être utilisé comme logique métier principale.
    """
    return str(uuid.uuid4())


def generate_numero_billet():
    """Génère un numéro unique et lisible pour le billet."""
    return f"EBILLET-{uuid.uuid4().hex[:10].upper()}"


def generate_cle_achat():
    """Clé interne de suivi d'achat."""
    return uuid.uuid4().hex


def generate_qr_code_base64(data: str) -> str:
    """
    Génère un QR code PNG encodé en base64 à partir d'une chaîne.
    """
    qr = qrcode.make(data)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("ascii")


# ---------- Modèle principal ----------

class EBillet(models.Model):
    """
    Représente un e-billet individuel, lié à une offre et un utilisateur.
    Le QR code est généré à partir de la cle_finale.
    """

    STATUTS = [
        ("VALIDE", "Valide"),
        ("UTILISE", "Utilisé"),
        ("ANNULE", "Annulé"),
        ("EXPIRE", "Expiré"),
    ]

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ebillets",
        help_text="Utilisateur propriétaire du billet.",
    )

    offre = models.ForeignKey(
        "offres.Offre",
        on_delete=models.CASCADE,
        related_name="ebillets",
        help_text="Offre ou pack lié à ce billet.",
    )

    validateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="billets_valides",
        help_text="Utilisateur (valideur) ayant scanné ou validé le billet.",
    )

    numero_billet = models.CharField(
        max_length=50,
        unique=True,
        default=generate_numero_billet,
        help_text="Numéro public unique du billet.",
    )

    date_achat = models.DateTimeField(
        auto_now_add=True,
        help_text="Date et heure d'achat du billet.",
    )

    cle_achat = models.CharField(
        max_length=64,
        default=generate_cle_achat,
        help_text="Identifiant interne d'achat.",
    )

    # Important :
    # - la vraie valeur doit être fournie par la logique métier
    #   dans commandes/services.py
    # - blank=True permet la création côté ORM avant affectation éventuelle
    cle_finale = models.CharField(
        max_length=64,
        unique=True,
        editable=False,
        db_index=True,
        blank=True,
        help_text=(
            "Clé finale dérivée (clé utilisateur + clé achat), "
            "utilisée pour le QR code et la validation."
        ),
    )

    qr_code = models.TextField(
        blank=True,
        help_text="Image du QR code encodée en base64.",
    )

    prix_paye = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Prix payé pour ce billet.",
    )

    statut = models.CharField(
        max_length=20,
        choices=STATUTS,
        default="VALIDE",
        db_index=True,
        help_text="Statut actuel du billet.",
    )

    date_utilisation = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Date et heure de validation/utilisation du billet.",
    )

    lieu_utilisation = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text="Lieu où le billet a été validé (ex: Entrée A).",
    )

    class Meta:
        db_table = "e_billet"
        indexes = [
            models.Index(fields=["numero_billet"]),
            models.Index(fields=["cle_finale"]),
            models.Index(fields=["statut"]),
            models.Index(fields=["date_utilisation"]),
        ]
        ordering = ["-date_achat"]
        verbose_name = "E-Billet"
        verbose_name_plural = "E-Billets"

    def save(self, *args, **kwargs):
        """
        Si une cle_finale existe mais que le QR n'est pas encore généré,
        on génère automatiquement le QR à partir de cle_finale.
        La cle_finale elle-même doit être fournie par la couche métier.
        """
        if self.cle_finale and not self.qr_code:
            self.qr_code = generate_qr_code_base64(self.cle_finale)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.numero_billet} - {self.utilisateur.username} ({self.statut})"