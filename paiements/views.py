# paiements/views.py
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from paiements.models import Commande
from paiements.serializers import CommandeSerializer
from billets.models import EBillet
from users.permissions import IsOwnerOrReadOnly


class CommandeViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les commandes :
    - Chaque utilisateur ne voit que ses commandes.
    - Vérifie le stock avant paiement.
    - Décrémente le stock après paiement.
    - Génère automatiquement les e-billets.
    """
    serializer_class = CommandeSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        """Limiter les commandes à l'utilisateur connecté, sauf pour les admins."""
        user = self.request.user
        if user.is_staff:
            return Commande.objects.all()
        return Commande.objects.filter(utilisateur=user)

    def perform_create(self, serializer):
        """Crée une commande à partir d’un panier non vide."""
        panier = serializer.validated_data["panier"]
        utilisateur = self.request.user

        if not panier.lignes.exists():
            raise ValueError("Impossible de créer une commande avec un panier vide.")

        montant_total = sum(ligne.sous_total for ligne in panier.lignes.all())

        serializer.save(
            utilisateur=utilisateur,
            montant_total=montant_total
        )

    def update(self, request, *args, **kwargs):
        """Empêcher la modification d'une commande déjà payée."""
        commande = self.get_object()
        if commande.statut_paiement == "PAYE":
            return Response(
                {"detail": "Impossible de modifier une commande déjà payée."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Empêcher la suppression d'une commande déjà payée."""
        commande = self.get_object()
        if commande.statut_paiement == "PAYE":
            return Response(
                {"detail": "Impossible de supprimer une commande déjà payée."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)

    # ---------------------------------------------------------------
    # 🔹 Action : Payer une commande
    # ---------------------------------------------------------------
    @action(detail=True, methods=["POST"], url_path="payer")
    def payer(self, request, pk=None):
        """
        Valide une commande comme payée :
        - Vérifie le stock disponible avant validation.
        - Décrémente le stock des offres.
        - Génère automatiquement les e-billets.
        """
        commande = self.get_object()

        # Vérifie si déjà payée
        if commande.statut_paiement == "PAYE":
            return Response(
                {"detail": "Cette commande est déjà payée."},
                status=status.HTTP_400_BAD_REQUEST
            )

        lignes_panier = commande.panier.lignes.select_related("offre")

        # ✅ Vérification du stock disponible
        for ligne in lignes_panier:
            offre = ligne.offre
            if not offre:
                return Response(
                    {"detail": f"Une ligne de panier est invalide (offre manquante)."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if offre.stock_disponible < ligne.quantite:
                return Response(
                    {"detail": f"Stock insuffisant pour {offre.nom_offre} "
                               f"(disponible : {offre.stock_disponible}, demandé : {ligne.quantite})."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # 💳 Simuler un paiement réussi
        commande.statut_paiement = "PAYE"
        commande.methode_paiement = request.data.get("methode_paiement", "Carte bancaire")
        commande.reference_paiement = request.data.get("reference_paiement", f"REF-{commande.numero_commande}")
        commande.date_paiement = timezone.now()
        commande.save(update_fields=["statut_paiement", "methode_paiement", "reference_paiement", "date_paiement"])

        # 🔻 Décrémente le stock des offres concernées
        for ligne in lignes_panier:
            offre = ligne.offre
            offre.stock_disponible -= ligne.quantite
            offre.save(update_fields=["stock_disponible"])

        # 🎟️ Génération automatique des e-billets
        billets_crees = []
        for ligne in lignes_panier:
            offre = ligne.offre
            for _ in range(ligne.quantite):
                billet = EBillet.objects.create(
                    utilisateur=commande.utilisateur,
                    offre=offre,
                    prix_paye=offre.prix,
                    statut="VALIDE"
                )
                billets_crees.append({
                    "id": billet.id,
                    "numero_billet": billet.numero_billet,
                    "qr_code": billet.qr_code,
                    "statut": billet.statut,
                })

        return Response({
            "message": "✅ Paiement validé avec succès. Billets générés.",
            "commande": commande.numero_commande,
            "billets": billets_crees
        }, status=status.HTTP_200_OK)

    # ---------------------------------------------------------------
    # 🔹 Action : Générer les billets manuellement
    # ---------------------------------------------------------------
    @action(detail=True, methods=["POST"], url_path="generer-billets")
    def generer_billets(self, request, pk=None):
        """
        Génère manuellement les e-billets d'une commande déjà payée.
        Évite les doublons si des billets existent déjà.
        """
        commande = self.get_object()

        if commande.statut_paiement != "PAYE":
            return Response(
                {"detail": "Impossible de générer des billets : commande non payée."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Empêcher la duplication
        if EBillet.objects.filter(utilisateur=commande.utilisateur, offre__in=commande.panier.lignes.values("offre")).exists():
            return Response(
                {"detail": "Les billets pour cette commande existent déjà."},
                status=status.HTTP_400_BAD_REQUEST
            )

        billets_crees = []
        for ligne in commande.panier.lignes.select_related("offre"):
            offre = ligne.offre
            for _ in range(ligne.quantite):
                billet = EBillet.objects.create(
                    utilisateur=commande.utilisateur,
                    offre=offre,
                    prix_paye=offre.prix,
                    statut="VALIDE"
                )
                billets_crees.append({
                    "id": billet.id,
                    "numero_billet": billet.numero_billet,
                    "qr_code": billet.qr_code,
                    "statut": billet.statut,
                })

        return Response({
            "message": "🎟️ Billets générés manuellement avec succès.",
            "commande": commande.numero_commande,
            "billets": billets_crees
        }, status=status.HTTP_201_CREATED)
