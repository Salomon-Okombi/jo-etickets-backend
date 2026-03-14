from django.db import transaction
from django.utils import timezone

from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Paiement
from .serializers import PaiementSerializer, CreatePaiementSerializer, ConfirmerPaiementSerializer


class IsOwnerOrStaff(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_authenticated and request.user.is_staff:
            return True
        return obj.utilisateur_id == getattr(request.user, "id", None)


class PaiementViewSet(viewsets.ModelViewSet):
    serializer_class = PaiementSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["statut", "provider", "commande"]
    search_fields = ["reference", "commande__numero_commande", "utilisateur__email", "utilisateur__username"]
    ordering_fields = ["date_creation", "date_confirmation", "montant", "statut"]
    ordering = ["-date_creation"]

    def get_queryset(self):
        user = self.request.user
        qs = Paiement.objects.select_related("utilisateur", "commande").all()
        if user.is_staff:
            return qs
        return qs.filter(utilisateur=user)

    def create(self, request, *args, **kwargs):
        ser = CreatePaiementSerializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)

        cmd = ser.validated_data["commande"]
        provider = ser.validated_data.get("provider", "MOCK")
        raw_payload = ser.validated_data.get("raw_payload")

        paiement = Paiement.objects.create(
            utilisateur=cmd.utilisateur,
            commande=cmd,
            montant=cmd.total,
            statut="INITIE",
            provider=provider,
            raw_payload=raw_payload,
        )

        out = PaiementSerializer(paiement, context={"request": request})
        return Response(out.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["POST"], url_path="confirmer")
    def confirmer(self, request, pk=None):
        paiement = self.get_object()

        ser = ConfirmerPaiementSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        success = ser.validated_data.get("success", True)
        raw_payload = ser.validated_data.get("raw_payload")
        ref = ser.validated_data.get("reference_paiement") or paiement.reference

        if paiement.statut != "INITIE":
            return Response({"detail": "Paiement déjà traité."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            paiement = Paiement.objects.select_for_update().get(pk=paiement.pk)
            cmd = paiement.commande

            if cmd.statut != "EN_ATTENTE":
                paiement.statut = "ANNULE"
                paiement.date_confirmation = timezone.now()
                paiement.raw_payload = raw_payload
                paiement.save(update_fields=["statut", "date_confirmation", "raw_payload"])
                return Response({"detail": "Commande non payable."}, status=status.HTTP_400_BAD_REQUEST)

            if not success:
                paiement.statut = "ECHEC"
                paiement.date_confirmation = timezone.now()
                paiement.raw_payload = raw_payload
                paiement.save(update_fields=["statut", "date_confirmation", "raw_payload"])
                return Response({"detail": "Paiement refusé (mock)."}, status=status.HTTP_400_BAD_REQUEST)

            paiement.statut = "SUCCES"
            paiement.date_confirmation = timezone.now()
            paiement.raw_payload = raw_payload
            paiement.save(update_fields=["statut", "date_confirmation", "raw_payload"])

            from commandes.services import payer_commande_et_generer_billets
            payer_commande_et_generer_billets(cmd, reference=ref)

        out = PaiementSerializer(Paiement.objects.get(pk=paiement.pk), context={"request": request})
        return Response(out.data, status=status.HTTP_200_OK)