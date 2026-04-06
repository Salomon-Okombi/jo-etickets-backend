# evenements/views_admin.py
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from .models import Evenement
from .serializers import EvenementAdminSerializer

class EvenementAdminViewSet(ModelViewSet):
    """
    CRUD 
    """
    queryset = Evenement.objects.all()
    serializer_class = EvenementAdminSerializer
    permission_classes = [IsAdminUser]