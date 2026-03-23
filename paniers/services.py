# paniers/services.py
from offres.models import Offre


class OffreNonDisponible(Exception):
    pass


def assert_offre_ajoutable(offre: Offre, qty: int):
    if qty <= 0:
        raise OffreNonDisponible("Quantité invalide.")
    if hasattr(offre, "est_disponible") and not offre.est_disponible:
        raise OffreNonDisponible("Offre indisponible.")
    if hasattr(offre, "restant") and qty > offre.restant:
        raise OffreNonDisponible("Stock insuffisant.")