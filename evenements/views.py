from rest_framework import viewsets, permissions, filters
from .models import Evenement
from .serializers import EvenementSerializer


class EvenementViewSet(viewsets.ModelViewSet):
    """
    CRUD complet des événements.
    Routes (via core/urls.py):
      /api/evenements/ (GET, POST)
      /api/evenements/<id>/ (GET, PATCH, DELETE)
    Accès réservé aux admins (is_staff=True).
    """
    queryset = Evenement.objects.all()
    serializer_class = EvenementSerializer
    permission_classes = [permissions.IsAdminUser]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nom", "discipline_sportive", "lieu_evenement", "statut", "description"]
    ordering_fields = ["date_evenement", "date_creation", "nom", "statut"]
    ordering = ["date_evenement"]