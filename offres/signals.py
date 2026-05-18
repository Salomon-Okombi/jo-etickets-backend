from django.db.models.signals import post_save
from django.dispatch import receiver

from evenements.models import Evenement
from offres.models import Offre, CategorieOffre


@receiver(post_save, sender=Evenement)
def recalc_offres_on_event_change(sender, instance: Evenement, created: bool, **kwargs):
    """
    Quand un événement change, on recalcule les offres associées.
    Utile surtout si prix_base a changé (prix des offres = dérivé).
    """
    # update_fields : optimisation si save(update_fields=...)
    update_fields = kwargs.get("update_fields")
    if update_fields is not None and not created:
        if "prix_base" not in update_fields:
            return

    # Re-save toutes les offres de l'événement -> Offre.save() recalcule prix
    qs = Offre.objects.filter(evenement=instance).select_related("categorie", "evenement")
    for o in qs:
        o.save()


@receiver(post_save, sender=CategorieOffre)
def recalc_offres_on_category_change(sender, instance: CategorieOffre, created: bool, **kwargs):
    """
    Quand une catégorie change (ex: nb_personnes), on recalcule les offres associées.
    """
    update_fields = kwargs.get("update_fields")
    if update_fields is not None and not created:
        # nb_personnes impacte directement le prix calculé
        if "nb_personnes" not in update_fields:
            return

    qs = Offre.objects.filter(categorie=instance).select_related("categorie", "evenement")
    for o in qs:
        o.save()