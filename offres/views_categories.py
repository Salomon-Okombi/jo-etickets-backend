# offres/views_categories.py
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from evenements.models import Evenement
from offres.models import Offre, CategorieOffre
from .serializers_categories import CategorieOffreSerializer


DEFAULT_QUOTA_BILLETS = 100
DEFAULT_DAYS = 60


class CategorieOffreViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public : lecture seule des catégories actives
    GET /api/offres/categories/
    GET /api/offres/categories/<id>/
    """
    serializer_class = CategorieOffreSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return (
            CategorieOffre.objects
            .filter(active=True)
            .order_by("ordre_affichage", "nom")
        )


class CategorieOffreAdminViewSet(viewsets.ModelViewSet):
    """
    Admin : CRUD catégories
    /api/offres/categories/admin/
    """
    serializer_class = CategorieOffreSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = CategorieOffre.objects.all().order_by("ordre_affichage", "nom")

    # ------------------------------------------------------------------
    # Propagation : catégorie globale => appliquer aux événements existants
    # ------------------------------------------------------------------
    def _apply_category_to_existing_events(self, cat: CategorieOffre):
        """
        Si la catégorie est globale + active, créer l'offre (événement × catégorie)
        pour tous les événements existants non expirés.

        IMPORTANT : on est en ViewSet admin => self.request.user disponible
        (nécessaire car Offre.createur est obligatoire).
        """
        if not cat.active:
            return
        if not getattr(cat, "auto_apply_all_events", False):
            return

        now = timezone.now()
        start = now - timedelta(minutes=5)
        end_default = now + timedelta(days=DEFAULT_DAYS)

        # Recommandé : n'appliquer que sur événements non expirés
        events = (
            Evenement.objects
            .filter(date_fin__gte=now)
            .order_by("date_debut")
        )

        for ev in events:
            # Fin de vente ne doit pas dépasser la fin de l'événement
            end = end_default
            if getattr(ev, "date_fin", None):
                end = min(end_default, ev.date_fin)

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
                    # Le champ prix est recalculé dans Offre.save() chez toi
                    # donc on n'a pas besoin de le renseigner ici.
                },
            )

    def perform_create(self, serializer):
        cat = serializer.save()
        self._apply_category_to_existing_events(cat)

    def perform_update(self, serializer):
        """
        Si une catégorie devient globale+active (ou était inactive puis activée),
        on peut l’appliquer aux événements existants.
        """
        before = self.get_object()
        before_active = before.active
        before_global = getattr(before, "auto_apply_all_events", False)

        cat = serializer.save()

        if cat.active and getattr(cat, "auto_apply_all_events", False) and (not before_active or not before_global):
            self._apply_category_to_existing_events(cat)

    # ------------------------------------------------------------------
    # Soft delete : désactivation au lieu de suppression si offres liées
    # ------------------------------------------------------------------
    def destroy(self, request, *args, **kwargs):
        """
        Suppression logique (soft delete) :
        - Si la catégorie est utilisée par des offres -> on désactive (active=False)
          et on désactive les offres liées (statut=INACTIVE), puis on renvoie 200.
        - Si aucune offre liée -> suppression réelle classique (204).
        """
        instance: CategorieOffre = self.get_object()

        # Grâce à ton modèle : Offre.categorie related_name="offres"
        offres_liees = instance.offres.all()

        if offres_liees.exists():
            with transaction.atomic():
                # 1) désactiver la catégorie
                instance.active = False
                instance.save(update_fields=["active", "date_modification"])

                # 2) désactiver les offres liées (recommandé)
                offres_liees.update(statut="INACTIVE")

            return Response(
                {
                    "detail": (
                        "Catégorie utilisée par des offres existantes : suppression remplacée par une désactivation "
                        "(active=false) et désactivation des offres liées (statut=INACTIVE)."
                    ),
                    "categorie_id": instance.id,
                    "offres_liees": offres_liees.count(),
                },
                status=status.HTTP_200_OK,
            )

        return super().destroy(request, *args, **kwargs)
