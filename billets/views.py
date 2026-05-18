from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.utils import timezone

from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend

from billets.models import EBillet
from billets.serializers import EBilletSerializer, EBilletAdminSerializer

import base64
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PIL import Image


class EBilletViewSet(viewsets.ModelViewSet):
    """
    Gestion sécurisée des e-billets.

    - Client : accès strictement limité à ses propres billets
    - Admin  : accès à tous les billets
    """
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = ["statut"]

    search_fields = [
        "numero_billet",
        "offre__nom_offre",
        "statut",
    ]

    ordering_fields = [
        "date_achat",
        "date_utilisation",
        "prix_paye",
        "statut",
        "numero_billet",
    ]

    ordering = ["-date_achat"]

    def get_queryset(self):
        user = self.request.user

        qs = EBillet.objects.select_related(
            "utilisateur",
            "offre",
            "validateur",
        )

        if user.is_staff:
            return qs

        return qs.filter(utilisateur=user)

    def get_serializer_class(self):
        if self.request.user.is_staff:
            return EBilletAdminSerializer
        return EBilletSerializer

    @action(detail=True, methods=["POST"], url_path="valider")
    def valider(self, request, pk=None):
        billet = self.get_object()

        if billet.statut != "VALIDE":
            return Response(
                {"detail": "Billet déjà utilisé ou invalide."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        billet.statut = "UTILISE"
        billet.lieu_utilisation = request.data.get("lieu_utilisation", "Non spécifié")
        billet.date_utilisation = timezone.now()
        billet.validateur = request.user
        billet.save()

        return Response(
            {"detail": "Billet validé avec succès."},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["POST"], url_path="valider-par-cle")
    def valider_par_cle(self, request):
        cle_finale = request.data.get("cle_finale")
        if not cle_finale:
            return Response(
                {"detail": "cle_finale manquante."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        billet = get_object_or_404(
            EBillet,
            cle_finale=cle_finale,
            statut="VALIDE",
        )

        billet.statut = "UTILISE"
        billet.lieu_utilisation = request.data.get("lieu_utilisation", "Non spécifié")
        billet.date_utilisation = timezone.now()
        billet.validateur = request.user
        billet.save()

        return Response(
            {"detail": "Billet validé avec succès."},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["GET"], url_path="telecharger")
    def telecharger(self, request, pk=None):
        billet = self.get_object()

        if not billet.qr_code:
            return Response(
                {"detail": "QR code non disponible."},
                status=status.HTTP_404_NOT_FOUND,
            )

        qr_data = base64.b64decode(billet.qr_code)
        response = HttpResponse(qr_data, content_type="image/png")
        response["Content-Disposition"] = (
            f'attachment; filename="{billet.numero_billet}.png"'
        )
        return response

    @action(detail=True, methods=["POST"], url_path="annuler")
    def annuler(self, request, pk=None):
        billet = self.get_object()

        if billet.statut != "VALIDE":
            return Response(
                {"detail": "Impossible d'annuler ce billet."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        billet.statut = "ANNULE"
        billet.save()

        return Response(
            {"detail": "Billet annulé."},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["GET"], url_path="pdf")
    def generer_pdf(self, request, pk=None):
        billet = self.get_object()

        if billet.statut not in ["VALIDE", "UTILISE"]:
            return Response(
                {"detail": "Billet invalide ou annulé."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        p.setFont("Helvetica-Bold", 16)

        x, y = 50, height - 50
        line_height = 25

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
        p.drawString(
            x,
            y,
            f"Date d'achat : {billet.date_achat.strftime('%d/%m/%Y %H:%M')}",
        )

        if billet.qr_code:
            try:
                qr_data = base64.b64decode(billet.qr_code)
                qr_image = Image.open(BytesIO(qr_data))
                if qr_image.mode != "RGB":
                    qr_image = qr_image.convert("RGB")
                p.drawInlineImage(qr_image, x, y - 220, width=200, height=200)
            except Exception:
                pass

        p.showPage()
        p.save()

        pdf = buffer.getvalue()
        buffer.close()

        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="{billet.numero_billet}.pdf"'
        )
        return response