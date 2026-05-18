from django.db.models import Sum, Max, Avg, Count
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import StatistiquesVente
from .serializers import StatistiquesVenteSerializer

# Imports pour l'endpoint overview (dashboard)
from evenements.models import Evenement
from offres.models import Offre
from billets.models import EBillet
from commandes.models import Commande


class StatistiquesVenteViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Lecture seule des statistiques de ventes par offre.
    Accès strictement réservé aux administrateurs.
    """
    queryset = StatistiquesVente.objects.select_related("offre").all()
    serializer_class = StatistiquesVenteSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        # Défense en profondeur
        if not self.request.user.is_staff:
            return StatistiquesVente.objects.none()
        return super().get_queryset()

    @action(detail=False, methods=["get"], url_path="global")
    def global_stats(self, request):
        """
        GET /api/statistiques/ventes/global/
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

        top_qs = qs.order_by("-nombre_ventes")[:5]
        top_5_offres = [
            {
                "offre_id": s.offre_id,
                "offre_nom": getattr(s.offre, "nom_offre", None),
                "nombre_ventes": s.nombre_ventes,
                "chiffre_affaires": str(s.chiffre_affaires),
            }
            for s in top_qs
        ]

        return Response({
            "ventes_totales": ventes_totales,
            "chiffre_affaires_total": str(ca_total),
            "panier_moyen": float(panier_moyen) if ventes_totales else 0,
            "nombre_offres_suivies": agg["nombre_offres_suivies"] or 0,
            "moyenne_ventes_jour_globale": float(agg["moyenne_ventes_jour_globale"] or 0),
            "derniere_mise_a_jour": agg["derniere_mise_a_jour"],
            "top_5_offres": top_5_offres,
        })


class StatsOverviewAPIView(APIView):
    """
    Endpoint attendu par le dashboard :
    GET /api/stats/overview/
    """
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        total_evenements = Evenement.objects.count()
        total_offres = Offre.objects.count()
        total_billets = EBillet.objects.count()

        ca = (
            Commande.objects
            .filter(statut="PAYEE")
            .aggregate(total=Sum("total"))
            .get("total") or 0
        )

        return Response({
            "evenements": total_evenements,
            "offres": total_offres,
            "reservations": total_billets,
            "chiffre_affaires": str(ca),
        })
