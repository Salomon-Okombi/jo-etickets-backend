# paniers/views_public.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from django.shortcuts import get_object_or_404
from django.db import transaction

from offres.models import Offre
from .models import Panier, LignePanier
from .serializers import PanierSerializer
from .services import assert_offre_ajoutable, OffreNonDisponible


def get_or_create_panier(request) -> Panier:
    # Auth user -> panier user (un panier ACTIF)
    if request.user and request.user.is_authenticated:
        panier, _ = Panier.objects.get_or_create(
            utilisateur=request.user,
            statut="ACTIF",
            defaults={"session_key": None},
        )
        return panier

    # Visiteur -> panier session
    if not request.session.session_key:
        request.session.save()

    panier, _ = Panier.objects.get_or_create(
        utilisateur=None,
        session_key=request.session.session_key,
        statut="ACTIF",
    )
    return panier


class PublicPanierView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        panier = get_or_create_panier(request)
        return Response(PanierSerializer(panier).data)


class PublicPanierAddItemView(APIView):
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):
        offer_id = request.data.get("offer_id")
        qty = int(request.data.get("qty", 1))

        if not offer_id:
            return Response({"detail": "offer_id requis."}, status=status.HTTP_400_BAD_REQUEST)

        offre = get_object_or_404(Offre.objects.select_related("evenement"), pk=offer_id)

        try:
            assert_offre_ajoutable(offre, qty)
        except OffreNonDisponible as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        panier = get_or_create_panier(request)

        ligne, created = LignePanier.objects.get_or_create(
            panier=panier,
            offre=offre,
            defaults={"quantite": qty},
        )

        if not created:
            new_qty = ligne.quantite + qty
            try:
                assert_offre_ajoutable(offre, new_qty)
            except OffreNonDisponible as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            ligne.quantite = new_qty
            ligne.save()
        else:
            ligne.save()  # calc prix_unitaire + sous_total + recalcul panier

        panier.refresh_from_db()
        return Response(PanierSerializer(panier).data, status=status.HTTP_201_CREATED)