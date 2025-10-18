# paniers/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Panier, LignePanier
from .serializers import PanierSerializer, LignePanierSerializer
from users.permissions import IsOwnerOrReadOnly  # 🔒 Permission personnalisée


class PanierViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des paniers utilisateurs.
    - Chaque utilisateur ne peut accéder qu’à ses propres paniers.
    - Vérifie le stock disponible avant tout ajout.
    - Autorise seulement le propriétaire à modifier ou supprimer.
    """
    queryset = Panier.objects.all()
    serializer_class = PanierSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        """
        Restreint la visibilité du panier à l'utilisateur connecté.
        Les administrateurs peuvent tout voir.
        """
        user = self.request.user
        if user.is_staff:
            return Panier.objects.all()
        return Panier.objects.filter(utilisateur=user)

    def perform_create(self, serializer):
        """
        Associe automatiquement l'utilisateur connecté lors de la création d’un panier.
        """
        serializer.save(utilisateur=self.request.user)

    @action(detail=False, methods=['post'], url_path='add')
    def ajouter_au_panier(self, request):
        """
        Ajouter une offre au panier actif de l'utilisateur.
        Crée un panier actif si aucun n'existe.
        Vérifie le stock avant ajout.
        """
        user = request.user
        data = request.data

        # Récupère ou crée le panier actif
        panier, _ = Panier.objects.get_or_create(utilisateur=user, statut='ACTIF')

        serializer = LignePanierSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        offre = serializer.validated_data['offre']
        quantite = serializer.validated_data['quantite']

        # 🧮 Vérification du stock disponible
        if offre.stock_disponible < quantite:
            return Response(
                {"detail": f"Stock insuffisant pour {offre.nom_offre} (disponible : {offre.stock_disponible})."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Vérifie si la ligne existe déjà
        ligne, created = LignePanier.objects.get_or_create(
            panier=panier,
            offre=offre,
            defaults={'quantite': quantite}
        )

        if not created:
            # Ajout de la quantité si la ligne existe déjà
            nouvelle_quantite = ligne.quantite + quantite

            if offre.stock_disponible < nouvelle_quantite:
                return Response(
                    {"detail": f"Stock insuffisant pour augmenter la quantité (max : {offre.stock_disponible})."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            ligne.quantite = nouvelle_quantite
            ligne.save()

        panier.recalc_montant()

        return Response(
            LignePanierSerializer(ligne).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['delete'], url_path='supprimer-ligne/(?P<ligne_id>[^/.]+)')
    def supprimer_ligne(self, request, pk=None, ligne_id=None):
        """
        Supprime une ligne spécifique du panier.
        """
        panier = self.get_object()
        try:
            ligne = panier.lignes.get(pk=ligne_id)
            ligne.delete()
            panier.recalc_montant()
            return Response({"detail": "Produit supprimé du panier"}, status=status.HTTP_200_OK)
        except LignePanier.DoesNotExist:
            return Response({"detail": "Ligne introuvable"}, status=status.HTTP_404_NOT_FOUND)
