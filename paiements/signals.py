# paiements/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from paiements.models import Commande
from analytics.models import StatistiquesVente
from django.db import transaction


@receiver(post_save, sender=Commande)
def mettre_a_jour_statistiques_vente(sender, instance, created, **kwargs):
    """
    Met à jour automatiquement les statistiques globales de ventes
    lorsqu'une commande est marquée comme PAYÉE.
    """
    # On ne déclenche pas lors de la création initiale (statut = ATTENTE)
    if created:
        return

    # Exécuter uniquement quand le paiement vient d’être validé
    if instance.statut_paiement == "PAYE":
        def _update_stats():
            total_ventes = Commande.objects.filter(statut_paiement="PAYE").count()
            montant_total = sum(
                c.montant_total for c in Commande.objects.filter(statut_paiement="PAYE")
            )

            # On suppose qu’on garde une seule ligne globale
            stats, _ = StatistiquesVente.objects.get_or_create(id=1)
            stats.total_commandes = total_ventes
            stats.montant_total = montant_total
            stats.save()

        # On s’assure d’exécuter après la transaction DB du paiement
        transaction.on_commit(_update_stats)
