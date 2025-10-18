# billets/views.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from billets.models import EBillet
from billets.serializers import EBilletSerializer
from users.permissions import IsOwnerOrReadOnly  # <-- ajout important
import base64
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PIL import Image


class EBilletViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les e-billets.
    - Filtrage automatique : chaque utilisateur ne voit que ses billets.
    - Permissions renforcées : seul le propriétaire peut modifier ou annuler.
    """
    serializer_class = EBilletSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        """
        Restreint les billets visibles à l'utilisateur connecté.
        """
        user = self.request.user
        return EBillet.objects.filter(utilisateur=user)

    @action(detail=True, methods=['POST'], url_path='valider')
    def valider(self, request, pk=None):
        """
        Valide un billet (action opérateur/valideur).
        """
        billet = self.get_object()
        if billet.statut != 'VALIDE':
            return Response({"detail": "Billet déjà utilisé ou annulé."}, status=status.HTTP_400_BAD_REQUEST)

        billet.statut = 'UTILISE'
        billet.lieu_utilisation = request.data.get('lieu_utilisation', 'Non spécifié')
        billet.date_utilisation = request.data.get('date_utilisation')
        billet.validateur = request.user
        billet.save()

        return Response({"detail": "Billet validé avec succès."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path='valider-par-cle')
    def valider_par_cle(self, request):
        """
        Validation d’un e-billet via sa clé finale (utilisée lors du scan QR).
        """
        cle_finale = request.data.get('cle_finale')
        billet = get_object_or_404(EBillet, cle_finale=cle_finale, statut='VALIDE')

        billet.statut = 'UTILISE'
        billet.lieu_utilisation = request.data.get('lieu_utilisation', 'Non spécifié')
        billet.date_utilisation = request.data.get('date_utilisation')
        billet.validateur = request.user
        billet.save()

        return Response({"detail": "Billet validé avec succès."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path='telecharger')
    def telecharger(self, request, pk=None):
        """
        Télécharge le QR code du billet au format PNG.
        """
        billet = self.get_object()
        if not billet.qr_code:
            return Response({"detail": "QR code non disponible."}, status=status.HTTP_404_NOT_FOUND)

        qr_data = base64.b64decode(billet.qr_code)
        response = HttpResponse(qr_data, content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="{billet.numero_billet}.png"'
        return response

    @action(detail=True, methods=['POST'], url_path='annuler')
    def annuler(self, request, pk=None):
        """
        Annule un billet encore valide.
        """
        billet = self.get_object()
        if billet.statut != 'VALIDE':
            return Response({"detail": "Impossible d'annuler ce billet."}, status=status.HTTP_400_BAD_REQUEST)

        billet.statut = 'ANNULE'
        billet.save()
        return Response({"detail": "Billet annulé."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path='pdf')
    def generer_pdf(self, request, pk=None):
        """
        Génère un e-billet au format PDF avec QR code intégré.
        """
        billet = self.get_object()

        if billet.statut not in ["VALIDE", "UTILISE"]:
            return Response({"detail": "Billet invalide ou annulé."}, status=status.HTTP_400_BAD_REQUEST)

        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        p.setFont("Helvetica-Bold", 16)

        x, y = 50, height - 50
        line_height = 25

        # Infos du billet
        p.drawString(x, y, f"E-Billet : {billet.numero_billet}")
        y -= line_height
        p.drawString(x, y, f"Utilisateur : {billet.utilisateur.username}")
        y -= line_height
        p.drawString(x, y, f"Offre : {billet.offre.nom_offre}")
        y -= line_height
        p.drawString(x, y, f"Prix payé : {billet.prix_paye} €")
        y -= line_height
        p.drawString(x, y, f"Statut : {billet.statut}")
        y -= line_height
        p.drawString(x, y, f"Date d'achat : {billet.date_achat.strftime('%d/%m/%Y %H:%M')}")

        # QR code
        if billet.qr_code:
            try:
                qr_data = base64.b64decode(billet.qr_code)
                qr_image = Image.open(BytesIO(qr_data))
                if qr_image.mode != 'RGB':
                    qr_image = qr_image.convert('RGB')
                p.drawInlineImage(qr_image, x, y - 220, width=200, height=200)
            except Exception:
                pass

        p.showPage()
        p.save()

        pdf = buffer.getvalue()
        buffer.close()

        response = HttpResponse(pdf, content_type="application/pdf")
        response['Content-Disposition'] = f'attachment; filename="{billet.numero_billet}.pdf"'
        return response
