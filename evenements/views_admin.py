# evenements/views_admin.py
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from .models import Evenement
from .serializers import EvenementAdminSerializer


class EvenementAdminViewSet(ModelViewSet):
    """
    API ADMIN
    /api/evenements/admin/
    """
    queryset = Evenement.objects.all().order_by("-date_creation")
    serializer_class = EvenementAdminSerializer
    permission_classes = [IsAdminUser]