# Last edited by you@example.com @ 05/06/26 21:11.
from decimal import Decimal
import base64
import hashlib
import hmac
import uuid
from io import BytesIO

import qrcode
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import Commande, LigneCommande
from offres.models import Offre
from billets.models import EBillet


DISCOUNT_THRESHOLD_BILLETS = 4
DISCOUNT_RATE = Decimal("0.03")  # 3% (mettre 0.05 pour 5% si besoin)


def _nb_personnes(offre: Offre) -> int:
    """
    Nombre de billets consommés par 1 pack (SOLO=1, DUO=2, FAMILLE=4...).
    On utilise la propriété offre.nb_personnes (qui lit categorie.nb_personnes).
    """
    nb = int(getattr(offre, "nb_personnes", 1) or 1)
    return nb if nb > 0 else 1


def _prix_pack(offre: Offre) -> Decimal:
    """
    Retourne le prix du pack (SOLO/DUO/FAMILLE) en Decimal.
    - si tu stockes prix en base : offre.prix
    - sinon : offre.prix_calcule (property) -> conversion
    """
    val = getattr(offre, "prix", None)
    if val is None:
        val = getattr(offre, "prix_calcule", "0.00")
    return Decimal(str(val)).quantize(Decimal("0.01"))


def _billets_demandes(offre: Offre, quantite_packs: int) -> int:
    """
    Convertit une quantité de packs en quantité de billets consommés.
    """
    return int(quantite_packs) * _nb_personnes(offre)


def generate_cle_achat() -> str:
    """
    Génère une clé d'achat unique pour un billet.
    """
    return uuid.uuid4().hex


def generate_cle_utilisateur(utilisateur) -> str:
    """
    Dérive une clé utilisateur stable à partir des données de l'utilisateur.
    On ne la stocke pas en base : on la calcule à la volée.
    """
    base = f"{utilisateur.id}:{utilisateur.username}:{utilisateur.email}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def generate_cle_finale(utilisateur, cle_achat: str) -> str:
    """
    Génère la clé finale dérivée de :
    - clé utilisateur
    - clé achat

    Version sécurisée avec HMAC.
    """
    cle_utilisateur = generate_cle_utilisateur(utilisateur)

    return hmac.new(
        key=settings.SECRET_KEY.encode("utf-8"),
        msg=f"{cle_utilisateur}:{cle_achat}".encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()


def generate_qr_code_base64(data: str) -> str:
    """
    Génère un QR code PNG en base64 à partir d'une chaîne.
    Le champ qr_code en base contiendra le contenu base64 du PNG.
    """
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


@transaction.atomic
def create_commande_from_items(utilisateur, items):
    """
    Crée une commande EN_ATTENTE à partir d'items.

    IMPORTANT :
    - On ne décrémente pas les quotas ici (sinon réservation sans paiement).
    - On vérifie seulement la disponibilité et le quota au moment de la création.
    """
    if not isinstance(items, list) or len(items) == 0:
        raise ValidationError("Liste d'articles vide.")

    cmd = Commande.objects.create(utilisateur=utilisateur, statut="EN_ATTENTE")

    total_avant_remise = Decimal("0.00")
    total_billets = 0

    for it in items:
        try:
            offre_id = int(it["offre"])
            qte_packs = int(it["quantite"])
        except Exception:
            raise ValidationError("Format items invalide (offre/quantite).")

        if offre_id <= 0 or qte_packs <= 0:
            raise ValidationError("Quantité invalide (doit être > 0).")

        # Lock sur l'offre (lecture cohérente si concurrence)
        offre = (
            Offre.objects
            .select_related("categorie", "evenement")
            .select_for_update()
            .get(id=offre_id)
        )

        if str(offre.statut).upper() != "ACTIVE":
            raise ValidationError("Offre inactive.")

        # Vendabilité métier (fenêtre vente, event publié, quota pack, etc.)
        if not getattr(offre, "est_disponible", False):
            raise ValidationError("Offre indisponible (hors vente ou expirée).")

        billets = _billets_demandes(offre, qte_packs)
        restant = int(getattr(offre, "quota_billets_restant", 0) or 0)

        if restant < billets:
            packs_dispo = restant // _nb_personnes(offre)
            raise ValidationError(
                f"Quota insuffisant pour {offre.nom_offre} (packs dispo: {packs_dispo})."
            )

        prix_unitaire = _prix_pack(offre)
        sous_total = (prix_unitaire * Decimal(qte_packs)).quantize(Decimal("0.01"))

        LigneCommande.objects.create(
            commande=cmd,
            offre=offre,
            quantite=qte_packs,           # quantite = packs
            prix_unitaire=prix_unitaire,  # prix du pack
            sous_total=sous_total,
        )

        total_avant_remise += sous_total
        total_billets += billets

    # Remise si >= 4 billets
    remise_montant = Decimal("0.00")
    if total_billets >= DISCOUNT_THRESHOLD_BILLETS:
        remise_montant = (total_avant_remise * DISCOUNT_RATE).quantize(Decimal("0.01"))

    total_final = (total_avant_remise - remise_montant).quantize(Decimal("0.01"))

    cmd.total = total_final
    cmd.save(update_fields=["total"])

    return cmd


@transaction.atomic
def payer_commande_et_generer_billets(cmd: Commande, reference: str | None = None):
    """
    Paiement mock + génération billets + décrément quota billets.

    - Transaction + select_for_update sur la commande et les offres => évite survente.
    - Idempotence : si déjà PAYEE, renvoie la commande sans rien refaire.
    - Génère pour chaque billet :
      - cle_achat
      - cle_finale (dérivée)
      - qr_code basé sur cle_finale
    """
    # Verrouille la commande (anti double clic)
    cmd = Commande.objects.select_for_update().get(pk=cmd.pk)

    if cmd.statut == "PAYEE":
        return cmd

    if cmd.statut != "EN_ATTENTE":
        raise ValidationError("Commande non payable.")

    lignes = cmd.lignes.select_related("offre", "offre__categorie").all()
    if not lignes.exists():
        raise ValidationError("Commande vide.")

    # Vérifier quotas + décrémenter
    for ligne in lignes:
        offre = (
            Offre.objects
            .select_for_update()
            .select_related("categorie", "evenement")
            .get(pk=ligne.offre_id)
        )

        # Revalider vendabilité (si l'offre a changé entre temps)
        if str(offre.statut).upper() != "ACTIVE" or not getattr(offre, "est_disponible", False):
            raise ValidationError(f"Offre indisponible : {offre.nom_offre}.")

        billets = _billets_demandes(offre, int(ligne.quantite))
        restant = int(getattr(offre, "quota_billets_restant", 0) or 0)

        if restant < billets:
            packs_dispo = restant // _nb_personnes(offre)
            raise ValidationError(
                f"Quota insuffisant pour {offre.nom_offre} (packs dispo: {packs_dispo})."
            )

        offre.quota_billets_restant = restant - billets
        offre.save(update_fields=["quota_billets_restant"])

    # Marquer commande payée (mock)
    cmd.statut = "PAYEE"
    cmd.date_paiement = timezone.now()
    cmd.reference_paiement = reference or f"MOCK-{cmd.numero_commande}"
    cmd.save(update_fields=["statut", "date_paiement", "reference_paiement"])

    # Générer billets : 1 billet = 1 personne
    for ligne in lignes:
        offre = ligne.offre
        billets = _billets_demandes(offre, int(ligne.quantite))

        for _ in range(billets):
            cle_achat = generate_cle_achat()
            cle_finale = generate_cle_finale(cmd.utilisateur, cle_achat)
            qr_code = generate_qr_code_base64(cle_finale)

            EBillet.objects.create(
                utilisateur=cmd.utilisateur,
                offre=offre,
                prix_paye=ligne.prix_unitaire,
                statut="VALIDE",
                cle_achat=cle_achat,
                cle_finale=cle_finale,
                qr_code=qr_code,
            )

    return cmd