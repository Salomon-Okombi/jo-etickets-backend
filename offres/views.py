from rest_framework import permissions, viewsets
from .models import Offre
from .serializers import OffreSerializer

class OffreViewSet(viewsets.ModelViewSet):
    queryset = Offre.objects.all()
    serializer_class = OffreSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAdminUser]  # ou ton SuperUserPermission
        else:
            permission_classes = [permissions.AllowAny]
        return [perm() for perm in permission_classes]

    def perform_create(self, serializer):
        # Associe automatiquement l'utilisateur connecté comme créateur
        serializer.save(createur=self.request.user)
