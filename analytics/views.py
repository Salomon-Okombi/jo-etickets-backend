# analytics/views.py
from django.db.models import Sum, Max, Avg, Count
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import StatistiquesVente
from .serializers import StatistiquesVenteSerializer


class StatistiquesVenteViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Lecture seule des statistiques de ventes par offre.
    Accès strictement réservé aux administrateurs.
    """
    queryset = StatistiquesVente.objects.select_related("offre").all()
    serializer_class = StatistiquesVenteSerializer
    permission_classes = [permissions.IsAdminUser]  # 🔐 admin-only

    def get_queryset(self):
        # Même si IsAdminUser protège déjà, on “blinde” côté queryset
        if not self.request.user.is_staff:
            return StatistiquesVente.objects.none()
        return super().get_queryset()

    @action(detail=False, methods=["get"], url_path="global")
    def global_stats(self, request):
        """
        GET /api/statistiques/ventes/global/
        Indicateurs globaux agrégés sur toutes les offres :
        - ventes_totales
        - chiffre_affaires_total
        - panier_moyen (CA / ventes)
        - nombre_offres_suivies
        - moyenne_ventes_jour_globale (moyenne du champ sur les offres)
        - derniere_mise_a_jour (max)
        - top_5_offres (par ventes)
        """
        qs = self.get_queryset()

        agg = qs.aggregate(
            ventes_totales=Sum("nombre_ventes"),
            chiffre_affaires_total=Sum("chiffre_affaires"),
            moyenne_ventes_jour_globale=Avg("moyenne_ventes_jour"),
            derniere_mise_a_jour=Max("date_derniere_maj"),
            nombre_offres_suivies=Count("id"),
        )

        ventes_totales = agg["ventes_totales"] or 0
        ca_total = agg["chiffre_affaires_total"] or 0
        panier_moyen = (ca_total / ventes_totales) if ventes_totales else 0

        # Top 5 par nombre de ventes
        top_qs = qs.order_by("-nombre_ventes")[:5]
        top_5_offres = [
            {
                "offre_id": s.offre_id,
                "offre_nom": getattr(s.offre, "nom_offre", None),
                "nombre_ventes": s.nombre_ventes,
                "chiffre_affaires": s.chiffre_affaires,
            }
            for s in top_qs
        ]

        return Response({
            "ventes_totales": ventes_totales,
            "chiffre_affaires_total": ca_total,
            "panier_moyen": panier_moyen,
            "nombre_offres_suivies": agg["nombre_offres_suivies"] or 0,
            "moyenne_ventes_jour_globale": agg["moyenne_ventes_jour_globale"] or 0,
            "derniere_mise_a_jour": agg["derniere_mise_a_jour"],
            "top_5_offres": top_5_offres,
        })
