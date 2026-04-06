from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework.authentication import SessionAuthentication
from .models import Evenement
from .serializers import EvenementListSerializer, EvenementDetailSerializer


class EvenementViewSet(ReadOnlyModelViewSet):
    """
    API publique – Boutique événements
    Aucune authentification requise.
    """

    #  NE PAS laisser JWT s’exécuter
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]

    queryset = Evenement.objects.filter(statut="PUBLIE")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return EvenementDetailSerializer
        return EvenementListSerializer