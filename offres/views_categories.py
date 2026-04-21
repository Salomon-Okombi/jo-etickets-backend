from rest_framework import viewsets, permissions
from .models import CategorieOffre
from .serializers_categories import CategorieOffreSerializer


class CategorieOffreViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public: lecture seule des catégories actives
    GET /api/offres/categories/
    GET /api/offres/categories/<id>/
    """
    serializer_class = CategorieOffreSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return CategorieOffre.objects.filter(active=True).order_by("ordre_affichage", "nom")


class CategorieOffreAdminViewSet(viewsets.ModelViewSet):
    """
    Admin: CRUD catégories
    /api/offres/categories/admin/
    """
    serializer_class = CategorieOffreSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = CategorieOffre.objects.all().order_by("ordre_affichage", "nom")