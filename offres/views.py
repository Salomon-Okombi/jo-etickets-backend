from django.db.models import F
from django.utils import timezone
from rest_framework import permissions, viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import Offre
from .serializers import OffrePublicSerializer, OffreAdminSerializer


class OffreViewSet(viewsets.ModelViewSet):
    """
    Endpoints :
    - Public (AllowAny) : list/retrieve => uniquement offres vendables
    - Admin (IsAdminUser) : create/update/delete => CRUD complet
    """
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # filtres DRF (query params)
    filterset_fields = ["evenement", "categorie", "statut"]

    search_fields = [
        "nom_offre",
        "categorie__code",
        "categorie__nom",
        "evenement__nom_evenement",
    ]

    # IMPORTANT : quota billets (plus de stock_disponible)
    ordering_fields = [
        "quota_billets_restant",
        "quota_billets_total",
        "date_creation",
        "date_debut_vente",
        "date_fin_vente",
    ]
    ordering = ["-date_creation"]

    def get_queryset(self):
        qs = Offre.objects.select_related("evenement", "categorie", "createur").all()

        # Public : on ne montre que les offres réellement vendables
        # (quota billets + fenêtre vente + événement publié/non expiré)
        if self.action in ["list", "retrieve"] and not (self.request.user and self.request.user.is_staff):
            now = timezone.now()

            qs = qs.filter(
                statut="ACTIVE",

                # fenêtre de vente
                date_debut_vente__lte=now,
                date_fin_vente__gte=now,

                # cohérence événement
                evenement__statut="PUBLIE",
                evenement__date_fin__gte=now,

                # quota billets : il faut avoir au moins un pack possible
                # => quota_billets_restant >= categorie.nb_personnes
                quota_billets_restant__gte=F("categorie__nb_personnes"),
            )

        return qs

    def get_permissions(self):
        # Public : lecture seule
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        # Admin : création / modification / suppression
        return [permissions.IsAdminUser()]

    def get_serializer_class(self):
        # Public : serializer enrichi (prix_calcule, est_disponible, packs dispo, etc.)
        if self.action in ["list", "retrieve"]:
            return OffrePublicSerializer
        # Admin : serializer CRUD (quota billets + dates + statut)
        return OffreAdminSerializer

    def perform_create(self, serializer):
        serializer.save(createur=self.request.user)
