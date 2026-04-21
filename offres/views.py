#offres/views.py
from rest_framework import permissions, viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import Offre
from .serializers import OffreSerializer


class OffreViewSet(viewsets.ModelViewSet):
    queryset = Offre.objects.select_related("evenement", "categorie", "createur").all()
    serializer_class = OffreSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["evenement", "categorie", "statut"]
    search_fields = ["nom_offre", "categorie__code", "categorie__nom", "evenement__nom_evenement"]
    ordering_fields = ["prix", "stock_disponible", "date_creation", "date_debut_vente", "date_fin_vente"]
    ordering = ["-date_creation"]

    def get_permissions(self):
        # Public read-only
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        # Admin-only write
        return [permissions.IsAdminUser()]

    def perform_create(self, serializer):
        serializer.save(createur=self.request.user)

