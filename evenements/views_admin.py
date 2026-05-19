# evenements/views_admin.py

from datetime import timedelta
from django.utils import timezone
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Evenement
from .serializers import EvenementAdminSerializer
from offres.models import CategorieOffre, Offre


DEFAULT_QUOTA_BILLETS = 100
DEFAULT_DAYS = 60


class EvenementAdminViewSet(ModelViewSet):
    """
    API ADMIN EVENEMENTS
    """

    permission_classes = [IsAdminUser]
    serializer_class = EvenementAdminSerializer

    # ✅ IMPORTANT -> permet upload image
    parser_classes = [MultiPartParser, FormParser]

    # ✅ IMPORTANT -> permet image_url dans serializer
    def get_serializer_context(self):
        return {"request": self.request}

    def get_queryset(self):
        return (
            Evenement.objects
            .all()
            .order_by("-date_debut", "-date_creation")
        )

    # =====================================================
    # CREATE
    # =====================================================

    def perform_create(self, serializer):
        ev = serializer.save()

        start = timezone.now() - timedelta(minutes=5)
        end = timezone.now() + timedelta(days=DEFAULT_DAYS)

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
                    "quota_billets_total": DEFAULT_QUOTA_BILLETS,
                    "quota_billets_restant": DEFAULT_QUOTA_BILLETS,
                    "date_debut_vente": start,
                    "date_fin_vente": end,
                    "statut": "ACTIVE",
                },
            )

    # =====================================================
    # UPDATE
    # =====================================================

    def perform_update(self, serializer):
        ev = serializer.save()

        changed_fields = set(serializer.validated_data.keys())

        if "prix_base" in changed_fields:
            offres = (
                Offre.objects
                .filter(evenement=ev)
                .select_related("evenement", "categorie")
            )

            for offre in offres:
                offre.save()