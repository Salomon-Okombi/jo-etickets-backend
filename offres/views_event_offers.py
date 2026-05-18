# offres/views_event_offers.py
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import Offre
from .serializers_event_offers import EventOfferAdminSerializer


class EventOfferAdminViewSet(viewsets.ModelViewSet):
    """
    Admin: gestion des offres par événement.

    Usage recommandé :
      GET    /api/offres/event-offers/?evenement=<event_id>
      POST   /api/offres/event-offers/              (payload contient evenement + categorie + quotas ...)
      PATCH  /api/offres/event-offers/<id>/
      DELETE /api/offres/event-offers/<id>/

    Notes:
    - L'offre = association (evenement × categorie) + quotas billets + fenêtre de vente + statut.
    - Prix est dérivé (pas en entrée).
    """

    permission_classes = [permissions.IsAdminUser]
    serializer_class = EventOfferAdminSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["evenement", "categorie", "statut"]
    search_fields = [
        "nom_offre",
        "categorie__code",
        "categorie__nom",
        "evenement__nom_evenement",
    ]
    ordering_fields = [
        "quota_billets_restant",
        "quota_billets_total",
        "date_creation",
        "date_debut_vente",
        "date_fin_vente",
    ]
    ordering = ["-date_creation"]

    def get_queryset(self):
        qs = (
            Offre.objects
            .select_related("evenement", "categorie", "createur")
            .all()
        )

        # Filtre principal : ?evenement=<id>
        evenement_id = self.request.query_params.get("evenement")
        if evenement_id:
            qs = qs.filter(evenement_id=evenement_id)

        return qs

    def perform_create(self, serializer):
        # createur obligatoire
        serializer.save(createur=self.request.user)
