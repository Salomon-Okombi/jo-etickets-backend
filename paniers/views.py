# paniers/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Panier, LignePanier
from .serializers import PanierSerializer, LignePanierSerializer

class PanierViewSet(viewsets.ModelViewSet):
    queryset = Panier.objects.all()
    serializer_class = PanierSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Chaque utilisateur ne voit que ses paniers
        return Panier.objects.filter(utilisateur=self.request.user)

    def perform_create(self, serializer):
        serializer.save(utilisateur=self.request.user)

    @action(detail=False, methods=['post'], url_path='add')
    def ajouter_au_panier(self, request):
        """
        Ajouter une offre au panier actif de l'utilisateur.
        Crée un panier actif si aucun n'existe.
        """
        user = request.user
        data = request.data

        # Récupère ou crée le panier actif
        panier, _ = Panier.objects.get_or_create(utilisateur=user, statut='ACTIF')

        serializer = LignePanierSerializer(data=data)
        if serializer.is_valid():
            # Vérifie si une ligne pour cette offre existe déjà
            ligne, created = LignePanier.objects.get_or_create(
                panier=panier,
                offre=serializer.validated_data['offre'],
                defaults={'quantite': serializer.validated_data['quantite']}
            )
            if not created:
                # Si existante, on ajoute la quantité
                ligne.quantite += serializer.validated_data['quantite']
                ligne.save()
            panier.recalc_montant()
            return Response(LignePanierSerializer(ligne).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='supprimer-ligne/(?P<ligne_id>[^/.]+)')
    def supprimer_ligne(self, request, pk=None, ligne_id=None):
        """Supprimer une ligne spécifique d'un panier"""
        panier = self.get_object()
        try:
            ligne = panier.lignes.get(pk=ligne_id)
            ligne.delete()
            panier.recalc_montant()  # met à jour le montant total
            return Response({"detail": "Produit supprimé du panier"}, status=status.HTTP_200_OK)
        except LignePanier.DoesNotExist:
            return Response({"detail": "Ligne introuvable"}, status=status.HTTP_404_NOT_FOUND)