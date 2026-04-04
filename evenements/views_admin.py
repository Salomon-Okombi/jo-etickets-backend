from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from .models import Evenement
from .serializers import EvenementDetailSerializer


class EvenementAdminViewSet(ModelViewSet):
    """
    API back-office événements.
    Réservée aux administrateurs.
    CRUD complet.
    """

    queryset = Evenement.objects.all()
    serializer_class = EvenementDetailSerializer
    permission_classes = [IsAdminUser]