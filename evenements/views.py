from django.utils import timezone
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Evenement
from .serializers import (
    EvenementListSerializer,
    EvenementDetailSerializer,
    EvenementHomeSerializer,
)


class EvenementViewSet(ReadOnlyModelViewSet):
    """
    API publique des événements

    Règles métier :
    - seuls les événements PUBLIE sont visibles
    - un événement expiré (date_fin < now) est automatiquement ARCHIVE
    - les événements à venir et en cours sont visibles publiquement
    """

    permission_classes = [AllowAny]

    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields = [
        "nom_evenement",
        "discipline",
        "lieu",
        "description_courte",
        "description_longue",
    ]

    ordering_fields = [
        "date_creation",
        "date_debut",
        "date_fin",
    ]

    def get_queryset(self):
        now = timezone.now()

        # Archivage automatique des événements expirés
        # (Optionnel: tu peux déplacer ça dans un cron/commande, mais ici c'est OK)
        Evenement.objects.filter(
            statut="PUBLIE",
            date_fin__lt=now
        ).update(statut="ARCHIVE")

        # Tous les événements publiés non expirés (à venir ou en cours)
        return (
            Evenement.objects.filter(
                statut="PUBLIE",
                date_fin__gte=now
            ).order_by("date_debut")
        )

    def get_serializer_class(self):
        if self.action == "retrieve":
            return EvenementDetailSerializer
        if self.action == "latest":
            return EvenementHomeSerializer
        return EvenementListSerializer

    @action(detail=False, methods=["get"], url_path="latest")
    def latest(self, request):
        """
        GET /api/evenements/latest/
        Retourne les 3 prochains événements publiés non expirés
        (à venir ou en cours)
        """
        now = timezone.now()

        events = (
            Evenement.objects.filter(
                statut="PUBLIE",
                date_fin__gte=now
            )
            .order_by("date_debut")[:3]
        )

        serializer = EvenementHomeSerializer(
            events,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)