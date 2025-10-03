from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from billets.models import EBillet
from paiements.models import Commande
from paiements.serializers import CommandeSerializer  # si tu en as un

class CommandeViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les commandes"""
    
    queryset = Commande.objects.all()
    serializer_class = CommandeSerializer  # ou ton serializer existant

    @action(detail=True, methods=['POST'], url_path='generer-billets')
    def generer_billets(self, request, pk=None):
        try:
            commande = self.get_object()
        except Commande.DoesNotExist:
            return Response({"detail": "Commande introuvable"}, status=status.HTTP_404_NOT_FOUND)

        panier = commande.panier
        lignes = panier.lignes.all()

        if not lignes:
            return Response({"detail": "Le panier est vide"}, status=status.HTTP_400_BAD_REQUEST)

        billets_crees = []

        for ligne in lignes:
            for _ in range(ligne.quantite):
                billet = EBillet.objects.create(
                    utilisateur=commande.utilisateur,
                    offre=ligne.offre,
                    prix_paye=ligne.sous_total / ligne.quantite,  # prix par billet
                    statut='VALIDE'
                )
                billets_crees.append({
                    "id": billet.id,
                    "numero_billet": billet.numero_billet,
                    "statut": billet.statut,
                    "cle_finale": billet.cle_finale
                })

        return Response({"billets": billets_crees}, status=status.HTTP_201_CREATED)
