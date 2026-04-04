from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import AllowAny
from .models import Evenement
from .serializers import (
    EvenementListSerializer,
    EvenementDetailSerializer,
)

class EvenementViewSet(ReadOnlyModelViewSet):
    """
    Accès public en lecture.
    Utilisé pour la boutique événements.
    """

    permission_classes = [AllowAny]

    queryset = Evenement.objects.filter(statut="PUBLIE")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return EvenementDetailSerializer
        return EvenementListSerializer