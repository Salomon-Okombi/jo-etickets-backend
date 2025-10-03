# billets/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from billets.models import EBillet
from billets.serializers import EBilletSerializer
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
import base64

class EBilletViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les e-billets.
    """
    queryset = EBillet.objects.all()
    serializer_class = EBilletSerializer

    def get_queryset(self):
        """
        Limite les billets à ceux de l'utilisateur connecté pour les endpoints list.
        """
        user = self.request.user
        if self.action == 'list':
            return EBillet.objects.filter(utilisateur=user)
        return EBillet.objects.all()

    @action(detail=True, methods=['POST'], url_path='valider')
    def valider(self, request, pk=None):
        """
        Valider un e-billet par id.
        """
        billet = self.get_object()
        if billet.statut != 'VALIDE':
            return Response({"detail": "Billet déjà utilisé ou annulé."}, status=status.HTTP_400_BAD_REQUEST)
        
        billet.statut = 'UTILISE'
        billet.lieu_utilisation = request.data.get('lieu_utilisation', 'Non spécifié')
        billet.date_utilisation = request.data.get('date_utilisation', None)
        billet.validateur = request.user
        billet.save()
        return Response({"detail": "Billet validé avec succès."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path='valider')
    def valider_cle(self, request):
        """
        Valider un e-billet via la cle_finale.
        """
        cle_finale = request.data.get('cle_finale')
        billet = get_object_or_404(EBillet, cle_finale=cle_finale)

        if billet.statut != 'VALIDE':
            return Response({"detail": "Billet déjà utilisé ou annulé."}, status=status.HTTP_400_BAD_REQUEST)

        billet.statut = 'UTILISE'
        billet.lieu_utilisation = request.data.get('lieu_utilisation', 'Non spécifié')
        billet.date_utilisation = request.data.get('date_utilisation', None)
        billet.validateur = request.user
        billet.save()

        return Response({"detail": "Billet validé avec succès."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path='telecharger')
    def telecharger(self, request, pk=None):
        """
        Télécharger un e-billet en tant qu'image PNG.
        """
        billet = self.get_object()

        if not billet.qr_code:
            return Response({"detail": "QR code non disponible."}, status=status.HTTP_404_NOT_FOUND)

        # Décoder le base64 en binaire
        qr_data = base64.b64decode(billet.qr_code)

        # Retourner le QR code comme fichier image téléchargeable
        response = HttpResponse(qr_data, content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="{billet.numero_billet}.png"'
        return response

    @action(detail=True, methods=['POST'], url_path='annuler')
    def annuler(self, request, pk=None):
        """
        Annuler un e-billet.
        """
        billet = self.get_object()
        if billet.statut != 'VALIDE':
            return Response({"detail": "Impossible d'annuler ce billet."}, status=status.HTTP_400_BAD_REQUEST)
        billet.statut = 'ANNULE'
        billet.save()
        return Response({"detail": "Billet annulé."}, status=status.HTTP_200_OK)
