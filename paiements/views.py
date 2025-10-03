# paiements/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from paiements.models import Commande
from paiements.serializers import CommandeSerializer
from billets.models import EBillet


class CommandeViewSet(viewsets.ModelViewSet):
    serializer_class = CommandeSerializer

    def get_queryset(self):
        """Limiter les commandes à l'utilisateur connecté"""
        return Commande.objects.filter(utilisateur=self.request.user)

    def perform_create(self, serializer):
        panier = serializer.validated_data["panier"]
        utilisateur = self.request.user

        # Vérifier que le panier n'est pas vide
        if not panier.lignes.exists():
            raise ValueError("Impossible de créer une commande avec un panier vide.")

        # Calcule le total du panier
        montant_total = sum(ligne.sous_total for ligne in panier.lignes.all())

        serializer.save(
            utilisateur=utilisateur,
            montant_total=montant_total
        )

    def update(self, request, *args, **kwargs):
        """Empêcher la modification d'une commande déjà payée"""
        commande = self.get_object()
        if commande.statut_paiement == "PAYE":
            return Response(
                {"detail": "Impossible de modifier une commande déjà payée."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Empêcher la suppression d'une commande déjà payée"""
        commande = self.get_object()
        if commande.statut_paiement == "PAYE":
            return Response(
                {"detail": "Impossible de supprimer une commande déjà payée."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["POST"], url_path="payer")
    def payer(self, request, pk=None):
        """
        Valider une commande comme payée et générer les e-billets
        """
        commande = self.get_object()

        if commande.statut_paiement != "ATTENTE":
            return Response({"detail": "Commande déjà traitée."}, status=status.HTTP_400_BAD_REQUEST)

        # Simuler un paiement réussi
        commande.statut_paiement = "PAYE"
        commande.methode_paiement = request.data.get("methode_paiement", "Carte bancaire")
        commande.reference_paiement = request.data.get("reference_paiement", "REF123")
        commande.save()

        # Génération automatique des e-billets
        billets_crees = []
        for ligne in commande.panier.lignes.all():
            for _ in range(ligne.quantite):
                billet = EBillet.objects.create(
                    utilisateur=commande.utilisateur,
                    offre=ligne.offre,
                    prix_paye=ligne.offre.prix,
                    statut="VALIDE"
                )
                billets_crees.append({
                    "id": billet.id,
                    "numero_billet": billet.numero_billet,
                    "qr_code": billet.qr_code,
                    "statut": billet.statut,
                })

        return Response({
            "message": "Paiement validé, billets générés.",
            "billets": billets_crees
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=["POST"], url_path="generer-billets")
    def generer_billets(self, request, pk=None):
        """
        Générer des billets manuellement (seulement si la commande est payée)
        """
        commande = self.get_object()

        if commande.statut_paiement != "PAYE":
            return Response(
                {"detail": "Impossible de générer des billets : commande non payée."},
                status=status.HTTP_400_BAD_REQUEST
            )

        billets_crees = []
        for ligne in commande.panier.lignes.all():
            for _ in range(ligne.quantite):
                billet = EBillet.objects.create(
                    utilisateur=commande.utilisateur,
                    offre=ligne.offre,
                    prix_paye=ligne.offre.prix,
                    statut="VALIDE"
                )
                billets_crees.append({
                    "id": billet.id,
                    "numero_billet": billet.numero_billet,
                    "qr_code": billet.qr_code,
                    "statut": billet.statut,
                })

        return Response({
            "message": "Billets générés manuellement.",
            "billets": billets_crees
        }, status=status.HTTP_201_CREATED)
