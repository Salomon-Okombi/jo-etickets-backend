from rest_framework import generics, permissions
from .models import Utilisateur
from .serializers import UtilisateurSerializer, UtilisateurRegisterSerializer

# Enregistrement d'un utilisateur
class UtilisateurRegisterView(generics.CreateAPIView):
    queryset = Utilisateur.objects.all()
    serializer_class = UtilisateurRegisterSerializer
    permission_classes = [permissions.AllowAny]

# Profil utilisateur (GET et PUT/PATCH)
class UtilisateurDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = UtilisateurSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Retourne l'utilisateur connecté
        return self.request.user
