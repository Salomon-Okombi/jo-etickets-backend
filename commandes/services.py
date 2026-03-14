from decimal import Decimal
from django.db import transaction
from django.utils import timezone

from .models import Commande, LigneCommande
from offres.models import Offre
from billets.models import EBillet


@transaction.atomic
def create_commande_from_items(utilisateur, items):
    cmd = Commande.objects.create(utilisateur=utilisateur, statut="EN_ATTENTE")

    total = Decimal("0.00")

    for it in items:
        offre_id = it["offre"]
        qte = int(it["quantite"])

        offre = Offre.objects.select_for_update().get(id=offre_id)

        if offre.statut != "ACTIVE":
            raise ValueError("Offre inactive.")

        if offre.stock_disponible < qte:
            raise ValueError("Stock insuffisant.")

        prix_unitaire = offre.prix
        sous_total = (prix_unitaire * qte)

        LigneCommande.objects.create(
            commande=cmd,
            offre=offre,
            quantite=qte,
            prix_unitaire=prix_unitaire,
            sous_total=sous_total,
        )

        total += sous_total

        offre.stock_disponible -= qte
        offre.save(update_fields=["stock_disponible"])

    cmd.total = total
    cmd.save(update_fields=["total"])

    return cmd


@transaction.atomic
def payer_commande_et_generer_billets(cmd: Commande, reference: str | None = None):
    if cmd.statut != "EN_ATTENTE":
        raise ValueError("Commande non payable.")

    cmd.statut = "PAYEE"
    cmd.date_paiement = timezone.now()
    cmd.reference_paiement = reference or f"MOCK-{cmd.numero_commande}"
    cmd.save(update_fields=["statut", "date_paiement", "reference_paiement"])

    # Génère les e-billets : quantité * nb_personnes
    lignes = cmd.lignes.select_related("offre").all()
    for ligne in lignes:
        nb = int(ligne.quantite) * int(ligne.offre.nb_personnes or 1)
        for _ in range(nb):
            EBillet.objects.create(
                utilisateur=cmd.utilisateur,
                offre=ligne.offre,
                prix_paye=ligne.prix_unitaire,
                statut="VALIDE",
            )

    return cmd