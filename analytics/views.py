from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import StatistiquesVente
from .serializers import StatistiquesVenteSerializer

class StatistiquesVenteViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les statistiques de ventes par offre.
    """
    queryset = StatistiquesVente.objects.all()
    serializer_class = StatistiquesVenteSerializer

    @action(detail=False, methods=["get"], url_path="global")
    def global_stats(self, request):
        """
        Endpoint GET /api/statistiques/ventes/global/
        Retourne les stats cumulées sur toutes les offres
        """
        total_ventes = sum(stat.nombre_ventes for stat in self.queryset)
        total_ca = sum(stat.chiffre_affaires for stat in self.queryset)

        return Response({
            "ventes_totales": total_ventes,
            "chiffre_affaires_total": total_ca
        })
