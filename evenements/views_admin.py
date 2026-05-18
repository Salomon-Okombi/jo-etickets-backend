# evenements/views_admin.py
from datetime import timedelta
from django.utils import timezone
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Evenement
from .serializers import EvenementAdminSerializer
from offres.models import CategorieOffre, Offre


DEFAULT_QUOTA_BILLETS = 100  # quota par défaut en billets (à ajuster)
DEFAULT_DAYS = 60


class EvenementAdminViewSet(ModelViewSet):
    """
    API ADMIN EVENEMENTS

    Routes :
    - GET /api/evenements/admin/
    - POST /api/evenements/admin/
    - GET /api/evenements/admin/{id}/
    - PATCH /api/evenements/admin/{id}/
    - DELETE /api/evenements/admin/{id}/
    """

    permission_classes = [IsAdminUser]
    serializer_class = EvenementAdminSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return (
            Evenement.objects
            .all()
            .order_by("-date_debut", "-date_creation")
        )

    def perform_create(self, serializer):
        """
        Lors de la création d’un événement via l’API admin,
        on crée automatiquement les offres UNIQUEMENT pour les catégories globales actives.
        (SOLO/DUO/FAMILLE par défaut)
        """
        ev = serializer.save()

        start = timezone.now() - timedelta(minutes=5)
        end = timezone.now() + timedelta(days=DEFAULT_DAYS)

        # IMPORTANT : uniquement catégories globales
        categories = (
            CategorieOffre.objects
            .filter(active=True, auto_apply_all_events=True)
            .order_by("ordre_affichage", "nom")
        )

        for cat in categories:
            Offre.objects.get_or_create(
                evenement=ev,
                categorie=cat,
                defaults={
                    "createur": self.request.user,
                    "nom_offre": f"{cat.code} - {ev.nom_evenement}",
                    "description": cat.description or "",
                    # Quota en billets (pas de stock en packs)
                    "quota_billets_total": DEFAULT_QUOTA_BILLETS,
                    "quota_billets_restant": DEFAULT_QUOTA_BILLETS,
                    "date_debut_vente": start,
                    "date_fin_vente": end,
                    "statut": "ACTIVE",
                },
            )

    def perform_update(self, serializer):
        """
        Lors d’une modification d’événement :
        - on sauvegarde l’événement
        - si prix_base change, on force un recalcul des offres
        """
        # on récupère les champs réellement modifiés
        changed_fields = set(getattr(serializer, "validated_data", {}).keys())
        ev = serializer.save()

        # Recalcul uniquement si prix_base est modifié (sinon pas nécessaire)
        if "prix_base" in changed_fields:
            offres = (
                Offre.objects
                .filter(evenement=ev)
                .select_related("evenement", "categorie")
            )
            for offre in offres:
                offre.save()