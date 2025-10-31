# paiements/views.py
from django.utils import timezone
from django.db import transaction
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
    - Chaque utilisateur ne voit que ses commandes (sauf admin).
    - Vérifie le stock avant paiement.
    - Fige le panier au moment de la commande.
    - Exécute le paiement dans une transaction atomique.
    - Génère les e-billets automatiquement.
    """
    serializer_class = CommandeSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    # -----------------------------------------------------------
    # 🔹 Récupération du queryset
    # -----------------------------------------------------------
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Commande.objects.all()
        return Commande.objects.filter(utilisateur=user)

    # -----------------------------------------------------------
    # 🔹 Création d’une commande à partir d’un panier
    # -----------------------------------------------------------
    def perform_create(self, serializer):
        """
        Crée une commande à partir d’un panier non vide.
        - Calcule le montant total.
        - Fige le panier (statut=VALIDE).
        - Initialise le paiement à ATTENTE.
        """
        panier = serializer.validated_data["panier"]
        utilisateur = self.request.user

        if not panier.lignes.exists():
            raise ValueError("Impossible de créer une commande avec un panier vide.")

        # Vérification de la validité des lignes
        if panier.lignes.filter(offre__isnull=True).exists():
            raise ValueError("Le panier contient une ou plusieurs lignes sans offre valide.")

        montant_total = sum(ligne.sous_total for ligne in panier.lignes.all())

        commande = serializer.save(
            utilisateur=utilisateur,
            montant_total=montant_total,
            statut_paiement="ATTENTE",
            methode_paiement=None,
            reference_paiement=None,
            date_paiement=None,
        )

        # On fige le panier pour éviter de le modifier après commande
        if panier.statut == "ACTIF":
            panier.statut = "VALIDE"
            panier.save(update_fields=["statut"])

        return commande

    # -----------------------------------------------------------
    # 🔹 Empêcher modification ou suppression d'une commande payée
    # -----------------------------------------------------------
    def _strip_payment_fields(self, data: dict):
        """Retire les champs de paiement lors d’un update/patch classique."""
        for k in ("statut_paiement", "methode_paiement", "reference_paiement", "date_paiement"):
            data.pop(k, None)

    def update(self, request, *args, **kwargs):
        self._strip_payment_fields(request.data.copy())
        commande = self.get_object()
        if commande.statut_paiement == "PAYE":
            return Response(
                {"detail": "Impossible de modifier une commande déjà payée."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        self._strip_payment_fields(request.data.copy())
        commande = self.get_object()
        if commande.statut_paiement == "PAYE":
            return Response(
                {"detail": "Impossible de modifier une commande déjà payée."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        commande = self.get_object()
        if commande.statut_paiement == "PAYE":
            return Response(
                {"detail": "Impossible de supprimer une commande déjà payée."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)

    # -----------------------------------------------------------
    # 🔹 Action : Payer une commande
    # -----------------------------------------------------------
    @action(detail=True, methods=["POST"], url_path="payer")
    def payer(self, request, pk=None):
        """
        Valide une commande comme payée :
        - Vérifie les offres et le stock (FOR UPDATE)
        - Décrémente le stock
        - Génère les e-billets
        - Rollback complet en cas d’erreur
        """
        commande = self.get_object()

        if commande.statut_paiement == "PAYE":
            return Response({"detail": "Cette commande est déjà payée."},
                            status=status.HTTP_400_BAD_REQUEST)

        from offres.models import Offre

        with transaction.atomic():
            try:
                # Récup lignes + contrôle d’intégrité
                lignes_panier = list(commande.panier.lignes.select_related("offre"))
                ids_invalides = [lp.id for lp in lignes_panier if lp.offre_id is None]
                if ids_invalides:
                    return Response(
                        {"detail": f"Lignes de panier invalides sans offre : {ids_invalides}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Verrouiller les offres
                offre_ids = [lp.offre_id for lp in lignes_panier]
                offres_lock = {
                    o.id: o for o in Offre.objects.select_for_update().filter(id__in=offre_ids)
                }

                # Vérif stock
                for lp in lignes_panier:
                    offre = offres_lock.get(lp.offre_id)
                    if not offre:
                        return Response(
                            {"detail": f"Offre introuvable pour la ligne #{lp.id}."},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    if offre.stock_disponible < lp.quantite:
                        return Response(
                            {"detail": f"Stock insuffisant pour {offre.nom_offre} "
                                       f"(disponible : {offre.stock_disponible}, demandé : {lp.quantite})."},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                # ✅ Marquer payé
                commande.statut_paiement = "PAYE"
                commande.methode_paiement = request.data.get("methode_paiement", "Carte bancaire")
                commande.reference_paiement = request.data.get(
                    "reference_paiement", f"REF-{commande.numero_commande}"
                )
                commande.date_paiement = timezone.now()
                commande.save(update_fields=[
                    "statut_paiement", "methode_paiement",
                    "reference_paiement", "date_paiement"
                ])

                # ✅ Décrémenter le stock
                for lp in lignes_panier:
                    offre = offres_lock[lp.offre_id]
                    nv = offre.stock_disponible - lp.quantite
                    offre.stock_disponible = nv if nv > 0 else 0
                    if hasattr(offre, "statut") and offre.stock_disponible == 0 and offre.statut != "EPUISEE":
                        offre.statut = "EPUISEE"
                        offre.save(update_fields=["stock_disponible", "statut"])
                    else:
                        offre.save(update_fields=["stock_disponible"])

                # ✅ Génère billets
                billets_crees = []
                for lp in lignes_panier:
                    offre = offres_lock[lp.offre_id]
                    for _ in range(lp.quantite):
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

            except Exception as e:
                # 🚨 Rollback automatique dans atomic()
                raise transaction.TransactionManagementError(
                    f"Erreur pendant le paiement : {str(e)}"
                )

        return Response({
            "message": "✅ Paiement validé avec succès. Billets générés.",
            "commande": commande.numero_commande,
            "billets": billets_crees
        }, status=status.HTTP_200_OK)

    # -----------------------------------------------------------
    # 🔹 Action : Générer manuellement les e-billets
    # -----------------------------------------------------------
    @action(detail=True, methods=["POST"], url_path="generer-billets")
    def generer_billets(self, request, pk=None):
        """
        Génère manuellement les e-billets d'une commande déjà payée.
        Évite les doublons si des billets existent déjà pour (utilisateur, offre).
        """
        commande = self.get_object()

        if commande.statut_paiement != "PAYE":
            return Response(
                {"detail": "Impossible de générer des billets : commande non payée."},
                status=status.HTTP_400_BAD_REQUEST
            )

        lignes_panier = commande.panier.lignes.select_related("offre")
        offre_ids = [lp.offre_id for lp in lignes_panier if lp.offre_id]
        if not offre_ids:
            return Response(
                {"detail": "Aucune offre valide liée au panier de la commande."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Vérifier si billets déjà existants
        deja = EBillet.objects.filter(
            utilisateur=commande.utilisateur,
            offre_id__in=offre_ids
        ).exists()
        if deja:
            return Response(
                {"detail": "Les billets pour cette commande existent déjà."},
                status=status.HTTP_400_BAD_REQUEST
            )

        billets_crees = []
        for lp in lignes_panier:
            if not lp.offre:
                continue
            for _ in range(lp.quantite):
                billet = EBillet.objects.create(
                    utilisateur=commande.utilisateur,
                    offre=lp.offre,
                    prix_paye=lp.offre.prix,
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
