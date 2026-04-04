from rest_framework.viewsets import ReadOnlyModelViewSet
from .models import Evenement
from .serializers import (
    EvenementListSerializer,
    EvenementDetailSerializer,
)

class EvenementViewSet(ReadOnlyModelViewSet):
    queryset = Evenement.objects.filter(statut="PUBLIE")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return EvenementDetailSerializer
        return EvenementListSerializer