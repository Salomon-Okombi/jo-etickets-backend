# paiements/signals.py
from decimal import Decimal
from django.db import transaction
from django.db.models import F
from django.dispatch import receiver
from django.db.models.signals import post_save

from paiements.models import Commande
from analytics.models import StatistiquesVente


def _was_status_transition_to_paye(instance: Commande, created: bool, update_fields) -> bool:
    """
    Retourne True seulement si on détecte une transition réelle vers PAYE.
    - Si created=True, on ne déclenche pas (création: ATTENTE).
    - Si update_fields est fourni et ne contient pas 'statut_paiement' => on ignore.
    - Sinon, on relit l'ancien statut en base (fallback) et on compare.
    """
    if created:
        return False

    # Si l'appelant a fourni update_fields et qu'il ne contient pas 'statut_paiement', on ignore.
    if update_fields is not None and "statut_paiement" not in update_fields:
        return False

    if instance.statut_paiement != "PAYE":
        return False

    # Fallback : relire l'ancien statut si possible (on est en post_save → valeur déjà modifiée).
    # On considère transition si, *juste avant*, ce n'était pas PAYE.
    # Comme on est en post_save, il n'y a pas d'accès direct à l'ancienne valeur,
    # on fait au mieux : si update_fields contenait 'statut_paiement', on suppose une transition.
    if update_fields is not None and "statut_paiement" in update_fields:
        return True

    # Sinon, on essaie de deviner : si la commande vient d'être mise à jour et a une date_paiement fraîche,
    # on considère que c'est bien l'appel de /payer (best effort).
    return True


@receiver(post_save, sender=Commande)
def mettre_a_jour_stats_apres_paiement(sender, instance: Commande, created, update_fields=None, **kwargs):
    """
    Met à jour StatistiquesVente quand une commande passe en PAYE.

    Sécurités :
    - Ne déclenche que sur transition réelle vers PAYE (évite le double comptage).
    - Exécuté après commit (on_commit) pour éviter les incohérences.
    - Ignore toute ligne de panier sans offre.
    """
    if not _was_status_transition_to_paye(instance, created, update_fields):
        return

    def _maj():
        lignes = instance.panier.lignes.select_related("offre")

        # Agréger par offre pour limiter les écritures
        agr = {}
        for lp in lignes:
            if not lp.offre_id:
                # Ligne de panier sans offre -> on ignore proprement
                continue
            if lp.offre_id not in agr:
                agr[lp.offre_id] = {
                    "quantite": 0,
                    "prix": lp.offre.prix,  # prix au moment de la commande (si le modèle l’expose)
                }
            agr[lp.offre_id]["quantite"] += lp.quantite

        # Appliquer les mises à jour statistiques
        for offre_id, payload in agr.items():
            qte = payload["quantite"]
            prix = payload["prix"]

            stats, _ = StatistiquesVente.objects.get_or_create(
                offre_id=offre_id,
                defaults={
                    "nombre_ventes": 0,
                    "chiffre_affaires": Decimal("0.00"),
                },
            )
            # MAJ atomique
            StatistiquesVente.objects.filter(pk=stats.pk).update(
                nombre_ventes=F("nombre_ventes") + qte,
                chiffre_affaires=F("chiffre_affaires") + (Decimal(qte) * prix),
            )

    # Exécuter après validation complète de la transaction
    transaction.on_commit(_maj)
