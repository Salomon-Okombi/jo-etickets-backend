from django.db import transaction
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Panier, LignePanier
from .serializers import PanierSerializer, LignePanierSerializer
from users.permissions import IsOwnerOrReadOnly
from offres.models import Offre


class PanierViewSet(viewsets.ModelViewSet):
    """
    Ancienne méthode :
    - Visiteur : panier local côté frontend (localStorage)
    - Au checkout : sync panier local -> panier serveur (utilisateur connecté)

    NB : Dans ce projet, 'quantite' côté panier = nombre de PACKS.
    Exemple : DUO (2 billets) avec quantite=2 => billets_demandes=4.
    """
    queryset = Panier.objects.all()
    serializer_class = PanierSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Panier.objects.all()
        return Panier.objects.filter(utilisateur=user)

    def perform_create(self, serializer):
        serializer.save(utilisateur=self.request.user)

    def _get_or_create_active_cart(self, user) -> Panier:
        """
        Garantit un seul panier ACTIF (garde le plus récent, expire les autres)
        """
        with transaction.atomic():
            panier = (
                Panier.objects
                .select_for_update()
                .filter(utilisateur=user, statut="ACTIF")
                .order_by("-date_creation")
                .first()
            )

            if not panier:
                panier = Panier.objects.create(utilisateur=user, statut="ACTIF")
            else:
                (
                    Panier.objects
                    .filter(utilisateur=user, statut="ACTIF")
                    .exclude(pk=panier.pk)
                    .update(statut="EXPIRE")
                )

            if panier.statut != "ACTIF":
                panier = Panier.objects.create(utilisateur=user, statut="ACTIF")

        return panier

    # ----------------------------
    # Helpers quota billets
    # ----------------------------

    def _billets_demandes(self, offre: Offre, quantite_packs: int) -> int:
        """
        Convertit une quantité de packs en nombre de billets consommés.
        SOLO=1, DUO=2, FAMILLE=4 (via offre.nb_personnes).
        """
        nb = int(getattr(offre, "nb_personnes", 1) or 1)
        if nb <= 0:
            nb = 1
        return int(quantite_packs) * nb

    def _check_quota(self, offre: Offre, quantite_packs: int):
        """
        Vérifie que le quota billets restant permet d'acheter quantite_packs packs.
        """
        billets = self._billets_demandes(offre, quantite_packs)

        # Offre doit être globalement vendable (statut + fenêtre de vente + cohérence événement)
        # (est_disponible vérifie au moins 1 pack vendable, mais pas forcément quantite_packs)
        if not getattr(offre, "est_disponible", False):
            return False, f"Offre indisponible : {offre.nom_offre}."

        restant = int(getattr(offre, "quota_billets_restant", 0) or 0)
        if restant < billets:
            nb = int(getattr(offre, "nb_personnes", 1) or 1)
            packs_dispo = restant // max(nb, 1)
            return (
                False,
                f"Quota insuffisant pour {offre.nom_offre} "
                f"(packs dispo: {packs_dispo}, billets restants: {restant})."
            )

        return True, None

    # ----------------------------
    # Endpoints
    # ----------------------------

    @action(detail=False, methods=["get"], url_path="actif")
    def actif(self, request):
        panier = self._get_or_create_active_cart(request.user)
        panier.refresh_from_db()
        return Response(PanierSerializer(panier).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="sync")
    def sync(self, request):
        """
        Body attendu:
        {
          \"items\": [
            {\"offre\": 12, \"quantite\": 2},
            {\"offre\": 18, \"quantite\": 1}
          ]
        }

        Comportement : REPLACE (remplace les lignes du panier actif)
        """
        user = request.user
        items = request.data.get("items", None)

        if not isinstance(items, list):
            return Response({"detail": "items doit être une liste"}, status=status.HTTP_400_BAD_REQUEST)

        panier = self._get_or_create_active_cart(user)

        with transaction.atomic():
            # Remplacement total des lignes
            panier.lignes.all().delete()

            for it in items:
                try:
                    offre_id = int(it.get("offre"))
                    quantite = int(it.get("quantite"))
                except Exception:
                    continue

                if offre_id <= 0 or quantite <= 0:
                    continue

                offre = (
                    Offre.objects
                    .select_related("categorie", "evenement")
                    .filter(pk=offre_id)
                    .first()
                )
                if not offre:
                    continue

                ok, msg = self._check_quota(offre, quantite)
                if not ok:
                    return Response({"detail": msg}, status=status.HTTP_400_BAD_REQUEST)

                LignePanier.objects.create(panier=panier, offre=offre, quantite=quantite)

            panier.recalc_montant()
            panier.refresh_from_db()

        return Response(PanierSerializer(panier).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="add")
    def ajouter_au_panier(self, request):
        user = request.user
        data = request.data

        panier = self._get_or_create_active_cart(user)

        serializer = LignePanierSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        offre = serializer.validated_data["offre"]
        quantite = serializer.validated_data["quantite"]

        ok, msg = self._check_quota(offre, quantite)
        if not ok:
            return Response({"detail": msg}, status=status.HTTP_400_BAD_REQUEST)

        ligne, created = LignePanier.objects.get_or_create(
            panier=panier,
            offre=offre,
            defaults={"quantite": quantite}
        )

        if not created:
            nouvelle_quantite = ligne.quantite + quantite
            ok2, msg2 = self._check_quota(offre, nouvelle_quantite)
            if not ok2:
                return Response({"detail": msg2}, status=status.HTTP_400_BAD_REQUEST)

            ligne.quantite = nouvelle_quantite
            ligne.save()

        panier.recalc_montant()
        panier.refresh_from_db()

        return Response(PanierSerializer(panier).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path=r"lignes/(?P<ligne_id>[^/.]+)/set")
    def set_qty(self, request, pk=None, ligne_id=None):
        panier = self.get_object()
        try:
            ligne = panier.lignes.get(pk=ligne_id)
        except LignePanier.DoesNotExist:
            return Response({"detail": "Ligne introuvable"}, status=status.HTTP_404_NOT_FOUND)

        try:
            quantite = int(request.data.get("quantite", 1))
        except Exception:
            return Response({"detail": "Quantité invalide"}, status=status.HTTP_400_BAD_REQUEST)

        if quantite <= 0:
            ligne.delete()
            panier.recalc_montant()
            panier.refresh_from_db()
            return Response(PanierSerializer(panier).data, status=status.HTTP_200_OK)

        ok, msg = self._check_quota(ligne.offre, quantite)
        if not ok:
            return Response({"detail": msg}, status=status.HTTP_400_BAD_REQUEST)

        ligne.quantite = quantite
        ligne.save()
        panier.recalc_montant()
        panier.refresh_from_db()
        return Response(PanierSerializer(panier).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path=r"lignes/(?P<ligne_id>[^/.]+)/inc")
    def inc_qty(self, request, pk=None, ligne_id=None):
        panier = self.get_object()
        try:
            ligne = panier.lignes.get(pk=ligne_id)
        except LignePanier.DoesNotExist:
            return Response({"detail": "Ligne introuvable"}, status=status.HTTP_404_NOT_FOUND)

        new_qty = ligne.quantite + 1
        ok, msg = self._check_quota(ligne.offre, new_qty)
        if not ok:
            return Response({"detail": msg or "Quota insuffisant."}, status=status.HTTP_400_BAD_REQUEST)

        ligne.quantite = new_qty
        ligne.save()
        panier.recalc_montant()
        panier.refresh_from_db()
        return Response(PanierSerializer(panier).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path=r"lignes/(?P<ligne_id>[^/.]+)/dec")
    def dec_qty(self, request, pk=None, ligne_id=None):
        panier = self.get_object()
        try:
            ligne = panier.lignes.get(pk=ligne_id)
        except LignePanier.DoesNotExist:
            return Response({"detail": "Ligne introuvable"}, status=status.HTTP_404_NOT_FOUND)

        new_qty = max(0, ligne.quantite - 1)
        if new_qty == 0:
            ligne.delete()
        else:
            # Ici pas besoin de re-check quota (on diminue), mais on garde cohérent
            ligne.quantite = new_qty
            ligne.save()

        panier.recalc_montant()
        panier.refresh_from_db()
        return Response(PanierSerializer(panier).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["delete"], url_path=r"supprimer-ligne/(?P<ligne_id>[^/.]+)")
    def supprimer_ligne(self, request, pk=None, ligne_id=None):
        panier = self.get_object()
        try:
            ligne = panier.lignes.get(pk=ligne_id)
            ligne.delete()
            panier.recalc_montant()
            panier.refresh_from_db()
            return Response(PanierSerializer(panier).data, status=status.HTTP_200_OK)
        except LignePanier.DoesNotExist:
            return Response({"detail": "Ligne introuvable"}, status=status.HTTP_404_NOT_FOUND)