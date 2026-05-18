from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError

from .models import Commande
from .serializers import CommandeSerializer, CreateCommandeSerializer
from .services import create_commande_from_items, payer_commande_et_generer_billets


class CommandeViewSet(viewsets.ModelViewSet):
    """
    ViewSet sécurisé pour les commandes :
    - CLIENT : accès uniquement à ses propres commandes
    - ADMIN  : accès à toutes les commandes
    """
    serializer_class = CommandeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = (
            Commande.objects
            .select_related("utilisateur")
            .prefetch_related("lignes__offre")
        )
        return qs if user.is_staff else qs.filter(utilisateur=user)

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        if not user.is_staff and obj.utilisateur_id != user.id:
            raise PermissionDenied("Accès interdit à cette commande.")
        return obj

    def create(self, request, *args, **kwargs):
        serializer = CreateCommandeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            cmd = create_commande_from_items(
                request.user,
                serializer.validated_data["items"]
            )
        except ValidationError as e:
            return Response({"detail": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            # Évite d'exposer l'exception interne au client
            return Response(
                {"detail": "Impossible de créer la commande (données invalides ou offre indisponible)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        out = CommandeSerializer(cmd, context={"request": request})
        return Response(out.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["POST"], url_path="payer")
    def payer(self, request, pk=None):
        cmd = self.get_object()
        ref = request.data.get("reference_paiement")

        try:
            cmd = payer_commande_et_generer_billets(cmd, reference=ref)
        except ValidationError as e:
            return Response({"detail": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(
                {"detail": "Paiement impossible (commande invalide ou quota insuffisant)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        out = CommandeSerializer(cmd, context={"request": request})
        return Response(out.data, status=status.HTTP_200_OK)