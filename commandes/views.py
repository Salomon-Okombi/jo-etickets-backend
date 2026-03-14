from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Commande
from .serializers import CommandeSerializer, CreateCommandeSerializer
from .services import create_commande_from_items, payer_commande_et_generer_billets


class CommandeViewSet(viewsets.ModelViewSet):
    serializer_class = CommandeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Commande.objects.prefetch_related("lignes__offre").select_related("utilisateur").all()
        if user.is_staff:
            return qs
        return qs.filter(utilisateur=user)

    def create(self, request, *args, **kwargs):
        serializer = CreateCommandeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            cmd = create_commande_from_items(request.user, serializer.validated_data["items"])
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        out = CommandeSerializer(cmd, context={"request": request})
        return Response(out.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["POST"], url_path="payer")
    def payer(self, request, pk=None):
        cmd = self.get_object()

        ref = request.data.get("reference_paiement")
        try:
            cmd = payer_commande_et_generer_billets(cmd, reference=ref)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        out = CommandeSerializer(cmd, context={"request": request})
        return Response(out.data, status=status.HTTP_200_OK)