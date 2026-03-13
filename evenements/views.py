# evenements/views.py
from rest_framework import viewsets, permissions, filters
from .models import Evenement
from .serializers import EvenementSerializer


class EvenementViewSet(viewsets.ModelViewSet):
    queryset = Evenement.objects.all()
    serializer_class = EvenementSerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nom", "discipline_sportive", "lieu_evenement", "statut", "description"]
    ordering_fields = ["date_evenement", "date_creation", "nom", "statut"]
    ordering = ["date_evenement"]

    def get_permissions(self):
        # Lecture publique
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        # Écriture admin only
        return [permissions.IsAdminUser()]