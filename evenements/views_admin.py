# evenements/views_admin.py
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Evenement
from .serializers import EvenementAdminSerializer


class EvenementAdminViewSet(ModelViewSet):
    """
    API ADMIN EVENEMENTS
    /api/evenements/admin/
    """
    queryset = Evenement.objects.all().order_by("-date_creation")
    serializer_class = EvenementAdminSerializer
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]