# evenements/views.py
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import AllowAny
from .models import Evenement
from .serializers import (
    EvenementListSerializer,
    EvenementDetailSerializer,
)


class EvenementViewSet(ReadOnlyModelViewSet):
    """
    API PUBLIQUE
    /api/evenements/
    """
    permission_classes = [AllowAny]
    queryset = Evenement.objects.filter(statut="PUBLIE").order_by("date_evenement")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return EvenementDetailSerializer
        return EvenementListSerializer